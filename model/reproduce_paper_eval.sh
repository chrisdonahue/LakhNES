for WORKDIR in ./pretrained/NES ./pretrained/NESAug ./pretrained/Lakh100k ./pretrained/Lakh200k ./pretrained/LakhNES
do
	python eval.py \
		--cuda \
		--data ../data/nesmdb_tx1 \
		--dataset nesmdb \
		--split all \
		--batch_size 10 \
		--tgt_len 128 \
		--ext_len 0 \
		--mem_len 896 \
		--work_dir ${WORKDIR} \
		--no_log
done
