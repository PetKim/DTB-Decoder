# DTB Decoder Documentation

## Introduction
This decoding script is an extension to the capabilities of [psi46/pxar](https://github.com/psi46)'s version of its decoder. The reason for the creation of this decoder is to address an overlooked (yet a fairly detrimental) issue seen when trying to read data from an irradiated TBM module; as soon as an error is detected, the program returns an error description and halts without giving the rest of the results. Additionally we are not able to analyze the raw data stream to precisely determine what happened. This decoder addresses both of these issues by giving the full decoded results of the data stream and giving the option to view the data stream if desired.

## Usage
An oscilloscope and having pxar already installed are the main requirements. We used an NI instrument to help transfer the data collected to our computer. It's suggested you use [NI MAX](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQwCAO&l=en-US). We need an oscilloscope because it allows us to extract the data stream from the digital testboard (DTB). We also still require the use of pxar since it contains the necessary commands that issues out the data stream. Once this is setup, all one needs to do is launch the pxar command line and issue the command ```adc```. This will send data through the oscilloscope and into your computer. 
