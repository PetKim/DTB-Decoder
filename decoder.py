import numpy as np
import math
import matplotlib.pyplot as plt
import pyvisa as visa
import os
import serial
import time
from scipy import stats
import re

def get_data(path):
    
    rm = visa.ResourceManager(path)
    addy = rm.list_resources()
    address = "".join(str(x) for x in addy)
    
    gpib = rm.open_resource(address)
    gpib.timeout = 100000
    gpib.clear()
    
    channel_2 = gpib.query('C2:INSPECT? "SIMPLE"')
    channel_3 = gpib.query('C3:INSPECT? "SIMPLE"')
    
    with open('m-q-5-31_ch2_output.txt', 'w') as output1:
        output1.write(channel_2)
    
    with open('m-q-5-31_ch3_output.txt', 'w') as output2:
        output2.write(channel_3)
        
    
    with open('m-q-5-31_ch2_output.txt', 'r',newline='\n') as file1:
        lines_2 = file1.readlines()
        j = len(lines_2)
        table_2 = np.linspace(0,1,(j-2)*6)
        i = 0
        
        for line in lines_2:
            data = np.fromstring(line, sep=' ')
            if((i>0) & (i<334)):
                table_2[(i-1)*6] = data[0]
                table_2[(i-1)*6+1] = data[1]
                table_2[(i-1)*6+2] = data[2]
                table_2[(i-1)*6+3] = data[3]
                table_2[(i-1)*6+4] = data[4]
                table_2[(i-1)*6+5] = data[5]
            i = i+1
            
        table_2_float = table_2.astype(float)
        
    with open('m-q-5-31_ch3_output.txt', 'r',newline='\n') as file2:
        lines_3 = file2.readlines()
        j = len(lines_3)
        table_3 = np.linspace(0,1,(j-2)*6)
        i = 0
        
        for line in lines_3:
            data = np.fromstring(line, sep=' ')
            if((i>0) & (i<334)):
                table_3[(i-1)*6] = data[0]
                table_3[(i-1)*6+1] = data[1]
                table_3[(i-1)*6+2] = data[2]
                table_3[(i-1)*6+3] = data[3]
                table_3[(i-1)*6+4] = data[4]
                table_3[(i-1)*6+5] = data[5]
            i = i+1
            
        table_3_float = table_3.astype(float)
    
    return table_2_float, table_3_float


def adjust_data(data):
    
    trim = []
    
    for i in range(len(data)):
        if data[i] < .1:
            trim.append(data[i])
            
    return trim

def get_bit_stream(data1, data2):
    
    data1np = np.array(data1)
    data2np = np.array(data2)
    data1_f = data1np.astype(float)
    data2_f = data2np.astype(float)
    data_sum = data1_f - data2_f
    
    for i in range(len(data_sum)):
        if data_sum[i] > 0:
            data_sum[i] = 1
        elif data_sum[i] < 0:
            data_sum[i] = 0
            
    return data_sum


def raw_bit_stream(bit_stream):
    
    for i in range(len(bit_stream)-5):
        if ((bit_stream[i] == 1) and (bit_stream[i+1] == 1) and (bit_stream[i+2] == 1) and (bit_stream[i+3] == 1) and (bit_stream[i+4] == 1) and (bit_stream[i+5] == 0)) or ((bit_stream[i] == 0) and (bit_stream[i+1] == 0) and (bit_stream[i+2] == 0) and (bit_stream[i+3] == 0) and (bit_stream[i+4] == 0) and (bit_stream[i+5] == 1)):
            fix = bit_stream[i:]
            break
            
    length = len(fix)
    for i in range(length):
        if length % 5 != 0:
            length = length - 1
        elif length % 5 == 0:
            fix_l = fix[:length]
            
    fix_np = np.array(fix_l)
    five_str = np.reshape(fix_np, (-1, 5))
    
    return five_str


def convert_raw(raw_bit):
    
    raw_bit_sum = np.sum(raw_bit, axis = 1)
    bin_stream = (raw_bit_sum > 0)*1 + (raw_bit_sum < 0)*0
    
    for i in range(len(bin_stream)):
        if ((bin_stream[i] == 1) and (bin_stream[i+1] == 1) and (bin_stream[i+2] == 1) and (bin_stream[i+3] == 1) and (bin_stream[i+4] == 1)) or ((bin_stream[i] == 0) and (bin_stream[i+1] == 0) and (bin_stream[i+2] == 0) and (bin_stream[i+3] == 0) and (bin_stream[i+4] == 0)):
            adj_bin_stream = bin_stream[i:]
            break
            
    length = len(adj_bin_stream)
    for i in range(length):
        if length % 5 != 0:
            length = length - 1
        elif length % 5 == 0:
            final_bin_stream = adj_bin_stream[:length]
            
    five_bin_stream_np = np.reshape(final_bin_stream, (-1, 5))
    five_bin_stream = np.array(five_bin_stream_np).tolist()
    
    return five_bin_stream


def nrzi_deconverter(five_bin):
    
    four_bin = []
    
    for i in range(len(five_bin)):
        if five_bin[i] == [1, 1, 1, 1, 1]:
            four_bin.append([1, 0, 1, 0])
        elif five_bin[i] == [0, 0, 0, 0, 0]:
            four_bin.append([1, 0, 1, 0])
        elif (five_bin[i] == [1, 0, 1, 0, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 0, 0, 0])
        elif (five_bin[i] == [0, 1, 1, 1, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 0, 0, 1])
        elif (five_bin[i] == [1, 1, 0, 0, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 0, 1, 0])
        elif (five_bin[i] == [1, 1, 0, 0, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 0, 1, 1])
        elif (five_bin[i] == [0, 1, 1, 0, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 1, 0, 0])
        elif (five_bin[i] == [0, 1, 1, 0, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 1, 0, 1])
        elif (five_bin[i] == [0, 1, 0, 1, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 1, 1, 0])
        elif (five_bin[i] == [0, 1, 0, 1, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([0, 1, 1, 1])
        elif (five_bin[i] == [1, 1, 1, 0, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 0, 0, 0])
        elif (five_bin[i] == [1, 1, 1, 0, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 0, 0, 1])
        elif (five_bin[i] == [1, 1, 0, 1, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 0, 1, 0])
        elif (five_bin[i] == [1, 1, 0, 1, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 0, 1, 1])
        elif (five_bin[i] == [1, 0, 0, 1, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 1, 0, 0])
        elif (five_bin[i] == [1, 0, 0, 1, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 1, 0, 1])
        elif (five_bin[i] == [1, 0, 1, 1, 1]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 1, 1, 0])
        elif (five_bin[i] == [1, 0, 1, 1, 0]) and (five_bin[i-1][4] == 0):
            four_bin.append([1, 1, 1, 1])
        elif (five_bin[i] == [0, 1, 0, 1, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 0, 0, 0])
        elif (five_bin[i] == [1, 0 ,0, 0, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 0, 0, 1])
        elif (five_bin[i] == [0, 0, 1, 1, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 0, 1, 0])
        elif (five_bin[i] == [0, 0, 1, 1, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 0, 1, 1])
        elif (five_bin[i] == [1, 0, 0, 1, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 1, 0, 0])
        elif (five_bin[i] == [1, 0, 0, 1, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 1, 0, 1])
        elif (five_bin[i] == [1, 0, 1, 0, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 1, 1, 0])
        elif (five_bin[i] == [1, 0, 1, 0, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([0, 1, 1, 1])
        elif (five_bin[i] == [0, 0, 0, 1, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 0, 0, 0])
        elif (five_bin[i] == [0, 0, 0, 1, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 0, 0, 1])
        elif (five_bin[i] == [0, 0, 1, 0, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 0, 1, 0])
        elif (five_bin[i] == [0, 0, 1, 0, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 0, 1, 1])
        elif (five_bin[i] == [0, 1, 1, 0, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 1, 0, 0])
        elif (five_bin[i] == [0, 1, 1, 0, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 1, 0, 1])
        elif (five_bin[i] == [0, 1, 0, 0, 0]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 1, 1, 0])
        elif (five_bin[i] == [0, 1, 0, 0, 1]) and (five_bin[i-1][4] == 1):
            four_bin.append([1, 1, 1, 1])

    four_bin_np = np.array(four_bin)
    
    return four_bin_np


def four_bin_splitter(four_bin):
    
    data_str_1 = []
    data_str_2 = []
    
    four_bin_stream = four_bin.flat
    for i in range(len(four_bin_stream)):
        if (i % 2) == 0:
            data_str_1.append(four_bin_stream[i])
        else:
            data_str_2.append(four_bin_stream[i])
            
    for i, n in enumerate(data_str_2):
        if n == 0:
            data_str_2[i] = 1
        elif n == 1:
            data_str_2[i] = 0
            
    length = len(data_str_1)
    for i in range(length):
        if length % 4 != 0:
            length = length - 1
        elif length % 4 == 0:
            data_str_1_trim = data_str_1[:length]
            data_str_2_trim = data_str_2[:length]
            
    stream_a = np.reshape(data_str_1_trim, (-1, 4))
    stream_b = np.reshape(data_str_2_trim, (-1, 4))
            
    return stream_a, stream_b


def adc(stream):
    
    list_stream = np.array(stream).tolist()
    adc_output = []
    count = 1
    
    for i in range(len(stream)-2):
        #TBM header
        if (list_stream[i] == [0, 1, 1, 1]) and (list_stream[i+1] == [1, 1, 1, 1]) and (list_stream[i+2] == [1, 1, 0, 0]):
            adc_output.append("HEADER DATA")
            
            #Convert the next 2 lines to integer for event counter
            event = []
            event.append(list_stream[i+3])
            event.append(list_stream[i+4])
            event_bin = []
            for array in event:
                for value in array:
                    event_bin.append(value)
            ev_string = ''.join(str(x) for x in event_bin)
            adc_output.append("Event counter: " + str(int(ev_string, 2)))
            
            #Get data ID and D
            data_id = []
            data_id.append(list_stream[i+5][0])
            data_id.append(list_stream[i+5][1])
            dat_string = ''.join(str(x) for x in data_id)
            adc_output.append("Data ID: " + str(int(dat_string, 2)))
            
            d = []
            d.append(list_stream[i+5][2:])
            d.append(list_stream[i+6])
            d_bin = []
            for array in d:
                for value in array:
                    d_bin.append(value)
            d_string = ''.join(str(x) for x in d_bin)
            adc_output.append("D: " + str(int(d_string, 2)))
            
            adc_output.append(" ")
            
        #ROC header
        if (list_stream[i] == [0, 1, 1, 1]) and (list_stream[i+1] == [1, 1, 1, 1]) and (list_stream[i+2][0] == 1) and (list_stream[i+2][1] == 0):
            adc_output.append("ROC HEADER")
            
            #Readback data for ROC
            rb_data = []
            rb_data.append(list_stream[i+2][2:])
            rb_data_bin = []
            for array in rb_data:
                for value in array:
                    rb_data_bin.append(value)
            rb_data_string = ''.join(str(x) for x in rb_data_bin)
            adc_output.append("ROC " + str(count) + " readback data: " + str(int(rb_data_string,2)))
            count = count+1
            
        #TBM trailer
        if (list_stream[i] == [0, 1, 1, 1]) and (list_stream[i+1] == [1, 1, 1, 1]) and (list_stream[i+2] == [1, 1, 1, 0]):
            adc_output.append(" ")
            adc_output.append("TBM DATA")
            
            #TBM trailer data
            if list_stream[i+3][0] == 1: #Checks for NTP
                adc_output.append("No Token Pass")
            
            if list_stream[i+3][1] == 1: #Checks for reset TBM
                adc_output.append("Reset TBM")
            
            if list_stream[i+3][2] == 1: #Checks for reset ROC
                adc_output.append("Reset ROC")
                
            if list_stream[i+4][0] == 1: #Checks for hard reset
                adc_output.append("Hard reset")
                
            if list_stream[i+4][1] == 1: #Checks for clear trigger center
                adc_output.append("Clear trigger center")
                
            if list_stream[i+4][2] == 1: #Checks for cal trigger
                adc_output.append("Cal trigger")
                
            if list_stream[i+4][3] == 1: #Checks for full stack
                adc_output.append("Stack full")
                
            if list_stream[i+5][0] == 1: #Checks for sent auto reset
                adc_output.append("Auto reset sent")
                
            if list_stream[i+5][1] == 1: #Checks for sent Pkam reset
                adc_output.append("Pkam reset sent")
                
            stack_count = []
            stack_count.append(list_stream[i+5][2:])
            stack_count.append(list_stream[i+6])
            stack_count_bin = []
            
            for array in stack_count:
                for value in array:
                    stack_count_bin.append(value)
                    
            stack_count_string = ''.join(str(x) for x in stack_count_bin)
            adc_output.append("Stack count: " + str(int(stack_count_string,2)))
    
    adc_output_np = np.array(adc_output)
    adc = np.reshape(adc_output_np, ( -1 , 1))
    
    return adc
