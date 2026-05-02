# Sequence Splicer and Translator Project  
This project contains the code necessary to generate a dashboard tool that allows users to analyze how the splicing of a gene affects the resulting mature mRNA transcript and protein sequence. The dashboard tool works by taking an input gene sequence (either through textbox or FASTA file), exon coordinates, and coding sequence coordinates to produce a mature mRNA sequence and translated protein sequence. These mRNA and protein sequences are displayed to the dashboard and made available to download as FASTA sequences. The dashboard also allows you to save jobs to a table that is maintained between sessions using Redis.  
![sequence processing](https://drive.google.com/file/d/1VzRCGs2A47IyYMUD_PFWWF-Yreaok1lo/view?usp=sharing)  
![saving and looking at previous sequences](https://drive.google.com/file/d/14G-nHbBepFebi2uicee699enqEZ7po9i/view?usp=sharing)  
## Launching the Dashboard  
While the necessary files are in your working directory, run the command ```make compose``` to close any containers running the dash app and Redis and relaunch them. ```make compose-down``` can be used to close the containers running the dash app and Redis.  
## Using the Dashboard  
### Inputs
Once the dashboard is running, you may input a DNA sequence either through the textbox or by uploading a valid, single sequence FASTA file using the button. The exon coordinates may be input in the textbox with the format "exon1StartPos,exon1EndPos;exon2StartPos,exon2EndPos;..." (e.g. 1,12;21,39), where the positions are relative to the input DNA sequence. The coding sequence coordinates may be input in the textbox with the format "cdsStartPos,cdsEndPos" (e.g. 4,15), where the positions are relative to the mature mRNA sequence. CDS length must be a multiple of 3.  
### Outputs  
Once all three inputs are given, click the "Process Sequence" button to generate the output mature mRNA and protein sequences. Click either "download" button to download the corresponding output sequence as a FASTA file. Use the "Reset" button to clear the output fields and enter different inputs to be processed.  
### Saving Jobs to Table  
Jobs can be saved to the table using the "Save Data to Table" button. This saves the inputs and outputs to a Redis database and displays them in the table across sessions. Jobs can be selected to view in expanded format below the table. The table and Redis database can be cleared using the "Reset Table" button.  
## Files and Directories
### sequence_processor.py  
The ```sequence_processor.py``` script is used to process an input sequence string or sequence from a FASTA file using input exon and coding sequence coordinates to print the mature mRNA sequence and protein sequence and make them available to download. If you run the script on its own, it takes command-line input loglevel (using ```-l```), sequence string (```-t```) or input FASTA file path (```-f```), exon coordinates (```-e```), coding sequence coordinates (```-c```), output mRNA FASTA file path (```-m```), or output protein FASTA file path (```-p```). Exon coordinates have the following format: "exon1_StartPos,exon1_EndPos;exon2_StartPos,exon2_EndPos;...". Coding sequence coordinates have the following format: "StartPos,EndPos".  
The script is imported by the ```app.py``` script to use its functions in processing inputs.  
### app.py  
This script creates the dashboard using Plotly Dash. The dashboard only functions correctly when run along with Redis in containers using ```make compose```.  
## requirements.txt  
This text file contains the necessary dependencies to run this dashboard and is used by the Dockerfile to install the necessary dependencies when building the image.  
### Dockerfile  
This file is used to build the image of the dashboard.  
### docker-compose.yml  
This file coordinates containers by pulling a Redis image from DockerHub and building a container from an image built using the Dockerfile.  
### Makefile  
This file defines "targets" that function as shortened commands used in place of ```docker compose``` commands. It allows you to run the dashboard using ```make compose``` as described above.  
### redis-data/  
This is the directory that is mounted to the Redis container to store data about saved jobs in the dashboard.  
### example_seq.fasta  
This is an example DNA sequence FASTA file that can be uploaded to the dashboard as input.  