# Sequence Splicer and Translator Project  
This project contains the code necessary to generate a dashboard tool that allows users to analyze how the splicing of a gene affects the resulting mature mRNA transcript and protein sequence. The dashboard tool works by taking an input gene sequence (either through textbox or FASTA file), exon coordinates, and coding sequence start and stop positions to produce a mature mRNA sequence and translated protein sequence. These mRNA and protein sequences are displayed to the dashboard and made available to download as FASTA sequences, with the displayed protein sequence also being annotated/highlighted with identified motifs.  
## Building the image from a Dockerfile  
While the Dockerfile is in your working directory, run the following code to build the image using the instructions in the Dockerfile.  
```bash
docker build -t <dockerhubusername>/<code>:<version> ./
```  
## Running containerized code from outside the container  
Below is information regarding how to run containerized code outside the container from the command line. Here is an example for reference:  
```bash
docker run --rm -v $PWD:/data -u $(id -u):$(id -g) colinsedgwick/sequence-splicer-translator:1.0 sequence_processor.py -l INFO -f /data/example_seq.fasta -e "1,12;21,39"
```  
An image to run the container from must be specified in the docker run command. ``` --rm ``` is used to remove the container after it is run.  
### Mounting data inside the container at runtime  
Using ``` -v $PWD:/data``` in you docker run command allows you to mount the input data from your working directory into /data within the container.  
### Running containerized code as specific user to avoid permission issues  
Running the containerized code without specifying the user will cause the owner of all generated output files to be root, which can cause permission issues. You can specify the user and group ID namespace to yours using ``` -u $(id -u):$(id -g)``` in your docker run command.  
## Scripts  
### sequence_processor.py  
The ```sequence_processor.py``` script is used to process an input sequence string or sequence from a FASTA file using input exon and coding sequence coordinates to print the mature mRNA sequence and protein sequence. It takes command-line input loglevel (using ```-l```), sequence string (```-t```) or FASTA file path (```-f```), exon coordinates (```-e```), and coding sequence coordinates (```-c```). Exon coordinates have the following format: "exon1_StartPos,exon1_EndPos;exon2_StartPos,exon2_EndPos;...". Coding sequence coordinates have the following format: "StartPos,EndPos". 
Example command using input sequence string:  
```bash
docker run --rm -v $PWD:/data -u $(id -u):$(id -g) colinsedgwick/sequence-splicer-translator:1.0 sequence_processor.py -l INFO -t ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG -e "1,12;21,39" -c "4,15"
```  
Example command using input FASTA file:  
```bash
docker run --rm -v $PWD:/data -u $(id -u):$(id -g) colinsedgwick/sequence-splicer-translator:1.0 sequence_processor.py -l INFO -f /data/example_seq.fasta -e "1,12;21,39" -c "4,15"
```  