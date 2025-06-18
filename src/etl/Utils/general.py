import os
def read_ticker_data(path): 
    '''
    Read raw data from text file (one ticker per line and .txt extension ) to a list
    Parametes
    --------
    path : str data file path

    Return
    ------ 
    a list of tickers

    '''
    with open(path, "r") as file:    
        lines = file.readlines()
        data = [line.strip() for line in lines]
    
    return data
def data_path(file_name):

    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir,"Data","Raw_data", f'{file_name}')
    return data_path
def batch(data,size = 100):
    '''
    Split a list into sublists each of length size
    Parameters
    ----------
    data : list
    size : int, optional (default is 100)

    Returns
    -------
    list of lists  
    '''
    if not data:
        return []
    
    count = 0
    chunk_list = []
    
    while count <= len(data): 
        chunk_list.append(data[count:count+size])
        count = count+size
    
    return chunk_list
 