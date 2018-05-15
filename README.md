PubMed Standardization
========================

This library takes the PubMed information stored in a working directory and standarize the information in two formats: json and plain text. 

The input directory contains the PubMeds *.gz files, so the first task executed for the library is unzip the files.  

After unziped the files, the standardization begins,  the xml's PubMed that contains the articles are readed and generate for each article a PMIDXXX.json and PMIDXXX.txt.

This library can be use as a step of a pipeline with the objective of generates the json and plain text of the PubMed articles.
 

========================

1.- Clone this repository 

    $ git clone https://github.com/javicorvi/pubmed_standardization.git
    
2.- Python 2.7 
	
	
3.- Third Party 
	
	pip install pandas
	pip install xmltodict
	pip install json

	
4.- Run the script
	
	To run the script just execute python pubmed_standardization -o /home/myname/pubmed_data 

5.- The container 
	
	If you just want to run the app without any kind of configuration you can do it 
	through the docker container is avaiblable in https://hub.docker.com/r/javidocker/pubmed_standardization/ 

	To run the docker: 
	
	docker run --rm -u $UID  -v /home/yourname/pubmed_data:/app/data pubmed_standardization

	the path home/yourname/pubmed_data will be the working directory in where the data will be downloaded.
