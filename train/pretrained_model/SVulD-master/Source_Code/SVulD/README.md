Here we provide fine-tune settings for SVulD, whose results are reported in the paper.

```shell
# Training
 python run.py \
    --output_dir saved_models/r_drop \
    --model_name_or_path unixcoder-base-nine \
    --do_train \
    --train_data_file ../../Database/SVulD/train.jsonl \
    --eval_data_file ../../Database/SVulD/valid.jsonl \
    --num_train_epochs 20 \
    --block_size 400 \
    --train_batch_size 32 \
    --eval_batch_size 32 \
    --learning_rate 2e-5 \
    --max_grad_norm 1.0 \
    --seed 99 \
    --r_drop
    
# Detect	
python run.py \
    --output_dir saved_models/r_drop \
    --model_name_or_path unixcoder-base-nine \
    --do_detect \
    --test_data_file ../../Database/SVulD/our_test_for_pretrain.jsonl \
    --block_size 400 \
    --eval_batch_size 16 \
    --seed 99
```
