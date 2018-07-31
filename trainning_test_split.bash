cat hepatotoxicity_corpus_pubmed/pubmed_result.xml.gz.xml.txt random_pubmed/random_result.xml.gz.xml.txt > data_set.txt
shuf -n 10000 data_set.txt > train_dev_10000.txt
shuf -n 1000 data_set.txt > test_dev_1000.txt
shuf -n 10000 data_set.txt > train_10000.txt
shuf -n 1000 data_set.txt > test_1000.txt




