import argparse

import tqdm
from transformers import AutoModel, AutoTokenizer, T5ForSequenceClassification, T5EncoderModel
from torch.utils.data import DataLoader,Dataset
import torch.nn as nn
import torch
import json
from transformers import AutoTokenizer, AutoModelForMaskedLM

class MatchDataset(Dataset):
    def __init__(self,file_path,tokenizer):
        self.tokenizer = tokenizer
        self.file_path = file_path
        print("Loading data....",file_path)
        with open(self.file_path, 'r',encoding="utf-8") as f:
            self.data = json.load(f)
    def __len__(self):
        return len(self.data)

    def code_standard(self,code):
        code = code.replace(' ', '')
        code = code.replace('\n', '')
        code = code.replace('\t', '')
        code = code.replace('\r', '')
        return code
    def __getitem__(self,idx):
        d=self.data[idx]
        label=d['target']
        code=self.code_standard( d['func_before'])
        code_input=self.tokenizer(code,return_tensors='pt',padding="max_length",truncation=True,max_length=512)
        for key,value in code_input.items():
            code_input[key] = value.flatten()
        temp=d.copy()
        temp.pop("func_before")
        if "respond_before" in d.keys():
            temp.pop("respond_before")
        return code_input,label,{**temp}
class SearchModel(nn.Module):
    def __init__(self,model_path):
        super(SearchModel,self).__init__()
        if model_path.find("codet5") !=-1:
            self.model=T5EncoderModel.from_pretrained(model_path)
        else:
            self.model = AutoModel.from_pretrained(model_path)
        self.fn=nn.Linear(self.model.config.hidden_size,1)
    def forward(self,code_input):

        code_embeddings = self.model(**code_input).last_hidden_state.mean(dim=1)
        res=self.fn(code_embeddings)
        return res
def calculate_metrics(test_more, file, prefix="",is_after=False):
    type=test_more["type"]
    pair_index=test_more["pair_index"]
    pred=test_more["pred"]
    before=0
    true_before=0
    after=0
    true_after=0
    non=0
    true_non=0
    pair_result={}
    for i in range(len(type)):
        t=type[i]
        p=pair_index[i]
        pr=pred[i]
        if p!=-1:
            if p not in pair_result.keys():
                pair_result[p]={"before":None,"after":None}
            pair_result[p][t]=pr
        if t=="before":
            before+=1
            if pr==1:
                true_before+=1
        elif t=="after":
            after+=1
            if pr==0:
                true_after+=1
        else:
            non+=1
            if pr==0:
                true_non+=1
    pair_metric=[0,0,0,0]
    '''
        0: before=0 after=0 P-B
        1: before=0 after=1 P-R
        2: before=1 after=0 P-C
        3: before=1 after=1 P-V
    '''
    for key,value in pair_result.items():
        # if value["before"]==None or value["after"]==None:continue
        assert value["before"]!=None and value["after"]!=None
        index=value["before"]*2+value["after"]
        pair_metric[index]+=1
    b=true_before/before
    a=true_after/after
    o=true_non/non
    bm_1=3/(1/b+1/a+1/o)
    total_pair=sum(pair_metric)
    pair_metric=[i/total_pair*100 for i in pair_metric]
    file.write(f"{prefix} Before Accuracy: {b*100:.4f}\n")
    file.write(f"{prefix} After Accuracy: {a*100:.4f}\n")
    file.write(f"{prefix} Non-vul Accuracy: {o*100:.4f}\n")
    file.write(f"{prefix} BM1: {bm_1:.4f}\n")
    file.write(f"{prefix} P-C {pair_metric[2]:.4f}\n")
    file.write(f"{prefix} P-V: {pair_metric[3]:.4f}\n")
    file.write(f"{prefix} P-B: {pair_metric[0]:.4f}\n")
    file.write(f"{prefix} P-R: {pair_metric[1]:.4f}\n")
    file.write("\n")

def train_epoch(model, device, train_loader,loss,optimizer):
    model.train()
    all_true_label,all_pred_label=[],[]
    loss_sum=0
    for code_input,label,_ in tqdm.tqdm(train_loader):
        for key,value in code_input.items():
            code_input[key] = value.to(device)
        label=label.to(device)
        output=model(code_input)
        l=loss(output.flatten(),label.float().flatten())
        loss_sum+=l.item()
        optimizer.zero_grad()
        l.backward()
        optimizer.step()
        true_label=label.detach().flatten().tolist()
        output=(output.sigmoid()>=0.5).detach().flatten().to(int).tolist()
        for i in true_label:
            all_true_label.append(i)
        for i in output:
            all_pred_label.append(i)
    return loss_sum/len(train_loader),all_true_label,all_pred_label
def eval(model, device, test_loader,loss):
    model.eval()
    k = 0
    all_true_label,all_pred_label=[],[]
    all_types=[]
    all_pair_index=[]
    loss_sum=0
    for code_input,label,more_infor in tqdm.tqdm(test_loader):
        for key, value in code_input.items():
            code_input[key] = value.to(device)
        label = label.to(device)
        output=model(code_input)
        l=loss(output.flatten(),label.float().flatten())
        loss_sum+=l.item()
        true_label=label.detach().flatten().tolist()
        output=(output.sigmoid()>=0.5).detach().flatten().to(int).tolist()
        for i in output:
            all_pred_label.append(i)
        all_types+=more_infor["type"]
        all_pair_index+=more_infor["pair_index"].tolist()
    return loss_sum/len(test_loader),{"type":all_types,"pair_index":all_pair_index,"pred":all_pred_label}
def train(model, device, train_loader, bigvul_loader,primevul_iter,optimizer, epoch, loss,result_file):
    for i in range(epoch):
        l_train,true_train,pred_train=train_epoch(model, device, train_loader, loss,optimizer)
        l_test_b,test_more=eval(model, device, bigvul_loader,loss)
        l_test_p,test_more_p=eval(model, device, primevul_iter,loss)
        if i ==0:
            with open(result_file, "w") as f:
                pass
        with open(result_file, "a") as f:
            f.write(f"Epoch: {i + 1}\n")
            f.write(f"Our Test Loss: {l_test_b:.4f}\n")
            calculate_metrics(test_more, f, prefix="Our Test ")
            f.write(f"Primevul Test Loss: {l_test_p:.4f}\n")
            calculate_metrics(test_more_p, f, prefix="Primevul Test ")
            f.write("=" * 50 + "\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path",
                        default='codet5-base',
                        type=str)
    parser.add_argument("--data_path",
                        default="data_pair/train/our_pairs.json",
                        type=str)
    parser.add_argument("--gpu", default=0, type=int)
    args = parser.parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    model=SearchModel(args.model_path)
    print(args.model_path)
    print(args.data_path)
    result_file=(args.model_path).split("/")[-1]+"_"+(args.data_path).split("_")[0]+"_result.txt"
    print(result_file)
    train_iter,bigvul_iter=DataLoader(dataset=MatchDataset(args.data_path, tokenizer),
                                    batch_size=64,
                                    shuffle=True),DataLoader(dataset=MatchDataset("data_pair/test/bigvul_test.json", tokenizer
                                                                                  ),batch_size=32,shuffle=True)
    primevul_iter=DataLoader(dataset=MatchDataset("data_pair/test/primevul_test.json", tokenizer
                                                                                  ),batch_size=32,shuffle=True)

    optimizer=torch.optim.Adam(params=model.parameters(),lr=1e-5,betas=(0.9,0.999))
    loss=torch.nn.BCEWithLogitsLoss()
    device=torch.device(f'cuda:{args.gpu}')
    model.to(device)
    train(model,device,train_iter,bigvul_iter,primevul_iter,optimizer,epoch=100,loss=loss,result_file=result_file)
