

  ```
# Training
cd linevul
python linevul_main.py \
    --output_dir=./saved_models/linevul \
    --model_type=roberta \
    --tokenizer_name=codebert-base \
    --model_name_or_path=codebert-base \
    --do_train \
    --train_data_file=../../../Database/SVulD/train.jsonl \
    --eval_data_file=../../../Database/SVulD/valid.jsonl \
    --epochs 20 \
    --block_size 400 \
    --train_batch_size 32 \
    --eval_batch_size 32 \
    --learning_rate 2e-5 \
    --max_grad_norm 1.0 \
    --evaluate_during_training \
    --seed 99
    
# Detect
cd linevul
python linevul_main.py \
    --output_dir=./saved_models/linevul \
    --model_type=roberta \
    --tokenizer_name=codebert-base \
    --model_name_or_path=codebert-base \
    --do_detect \
    --test_data_file=../../../Database/SVulD/our_test_for_pretrain.jsonl \
    --block_size 400 \
    --eval_batch_size 64 \
    --learning_rate 2e-5 \
    --max_grad_norm 1.0 \
    --seed 99
  ```
