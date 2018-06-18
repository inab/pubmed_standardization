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


4.- Sqlite 
	
	To control the updates of pubmed a sqlite database is generated to store the already downloaded files and standardized files. 
	In the previous step of the pipeline the downloaded information has to be completed.
	
	
5.- Run the script
	
	To run the script just execute python pubmed_standardization -p /home/myuser/config.properties
	
	The config.properties file contains the parameters for the execution
	
	[MAIN]
	output=/home/myuser/your_work_dir/pubmed_data/
	[DATABASE]
	url=sqlite:////home/yourname/your_work_dir/bio_databases.db
	
	To pass parameters individually:
	-o ----- > Output Directory
	-u ------> SQLITE Database URL
	
	Remember the database has to be created in the previous step in home/yourname/your_work_dir/ 

6.- The container 
	
	If you just want to run the app without any kind of configuration you can do it 
	through the docker container is avaiblable in https://hub.docker.com/r/inab/pubmed_standardization/ 

	The path home/yourname/your_work_dir will be the working directory in where the data will be downloaded, this is the configuration of a 
	Volumes for stored the data outside of the container and then standardized by this container.

	To run the docker: 
	
	1)  Wiht the default parameters: 
	    
	    docker run --rm -u $UID  -v /home/yourname/your_work_dir/:/app/data pubmed_standardization python pubmed_standardization.py -p config.properties

		The default config.properties its inside the container and has the following default parameters: 
		
		[MAIN]
		output=/app/data/pubmed_data/
		[DATABASE]
		url=sqlite:////app/data/bio_databases.db
	
		It's the most basic configuration, and it 's recommended to used in this way.
	
	2)  Passing specific parameters:
	
		docker run --rm -u $UID  -v /home/yourname/your_work_dir/:/app/data pubmed_standardization python pubmed_standardization.py -u sqlite:////app/data/bio_databases.db -o /app/data/pubmed_data/

	3) Passing specifig config.properties file:
	
		Put your own config file in the your working directory:  /home/yourname/your_work_dir/config.properties  
		
		docker run --rm -u $UID  -v /home/yourname/your_work_dir/:/app/data pubmed_standardization python pubmed_standardization.py -p /app/data/config_own.properties
		
		