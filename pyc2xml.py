import struct
from xml.dom import minidom
import sys
import time

intern_str = []

def main():
    a = open('./show.pyc')
    b = a.read()
    a.close()
    x = struct.unpack_from('c'*len(b),b)
    return x

def get_length(pyc,cursor):
    tmp = ''
    for i in range(cursor,cursor+4):
        tmp += pyc[i]
    y = struct.unpack('i',tmp)
    return y[0]


def parse_obj(pyc,cursor):
    figure = pyc[cursor]
    if figure not in "(itsNc{R":
        figure = '('
        cursor += 4
    figure = pyc[cursor]
    if figure == 'i':
        cursor += 5
        return get_length(pyc,cursor-4),cursor
    elif figure == 't' or figure == 's':
        cursor += 5
        length = get_length(pyc,cursor-4)
        tmp = figure + ' '
        for i in range(cursor,cursor+length):
            tmp += pyc[i]
        cursor += length
        if figure == 't':
            intern_str.append(tmp)
        return tmp,cursor
    elif figure == '(':
        cursor += 5
        tmp_list = []
        items = get_length(pyc,cursor-4)
        for i in range(items):
            one = parse_obj(pyc,cursor)
            cursor = one[1]
            tmp_list.append(one[0])
        return tmp_list,cursor
    elif figure == 'N':
        return None,cursor+1
    elif figure == 'R':
        return 'ref '+ intern_str[get_length(pyc,cursor+1)],cursor+5
    elif figure == 'c':
        return parse_code(pyc,cursor)
    else:
        return None,cursor+1

def parse_code(pyc,cursor):
    tmp_list = []
    cursor += 1
    a = get_length(pyc,cursor)
    cursor += 4
    b = get_length(pyc,cursor)
    cursor += 4
    c = get_length(pyc,cursor)
    cursor += 4
    flag = get_length(pyc,cursor)
    cursor += 5
    stringlen = get_length(pyc,cursor)
    cursor += stringlen
    cursor += 4
    figure = pyc[cursor]
    for i in range(8):
        if figure in "sti(NcR{":
            one = parse_obj(pyc,cursor)
            tmp_list.append(one[0])
            cursor = one[1]
        else:
            return None,cursor+1
    return tmp_list,cursor


class parse_pyc():
    def __init__(self,pycfile):
        self.pycfile = pycfile
        self.cursor = 26      #the starting of the co_code item

    def get_time(self):
        tmp_string = ''
        for i in range(4,8):
            tmp_string += self.pycfile[i]
        y = struct.unpack('i',tmp_string)
        return time.ctime(y[0])
    
    def get_all_args(self):
        arguments = []
        args_count = ''
        for i in range(3):
            for j in range(9,13):
                args_count += self.pycfile[i*4 + j]
            y = struct.unpack('i',args_count)
            arguments.append(y[0])
            args_count = ''
        return arguments

    def get_code(self):
        cursor = self.cursor
        self.cursor += 4 #the length is 4
        tmp = ''
        for i in range(cursor,cursor+4):
            tmp += self.pycfile[i]
        y = struct.unpack('i',tmp)
        self.cursor += y[0]
        return y[0]

    def get_consts(self):
        consts,self.cursor = parse_obj(self.pycfile,self.cursor)
        #print "here %d"%self.cursor
        return consts

    def get_names(self):
        names,self.cursor = parse_obj(self.pycfile,self.cursor)
        return names

    def get_varnames(self):
        varnames,self.cursor =  parse_obj(self.pycfile,self.cursor)
        return varnames

    def get_freevars(self):
        freevars,self.cursor = parse_obj(self.pycfile,self.cursor)
        return freevars

    def get_cellvars(self):
        cellvars,self.cursor = parse_obj(self.pycfile,self.cursor)
        return cellvars

    def get_filename(self):
        filename,self.cursor = parse_obj(self.pycfile,self.cursor)
        return filename

    def get_lineno(self):
        lineno,self.cursor = parse_obj(self.pycfile,self.cursor)
        return lineno

    def get_lnotab(self):
        lnotab,self.cursor = parse_obj(self.pycfile,self.cursor)
        return list(lnotab)

def output(parsed):
    doc = minidom.Document()
    pycfile = doc.createElement("Pycfile")
    codeobj = doc.createElement('CodeObject')
    argCount = doc.createElement('argCount')
    args_total = parsed.get_all_args()
    argCount.setAttribute('value',str(args_total[0]))
    codeobj.appendChild(argCount)
    localCount = doc.createElement("localCount")
    localCount.setAttribute('value',str(args_total[1]))
    codeobj.appendChild(localCount)
    stackSize = doc.createElement('stackSize')
    stackSize.setAttribute("value",str(args_total[2]))
    codeobj.appendChild(stackSize)              #all the arguments
    
    code_len = parsed.get_code()
    code = doc.createElement('code')
    code_str = doc.createElement('str')
    code_str.setAttribute('length',str(code_len))
    code_str.setAttribute('value','binary')
    code.appendChild(code_str)
    codeobj.appendChild(code)                   #add the code seg

    consts = doc.createElement('consts')
    parsed_const = parsed.get_consts()
    add_subitems(parsed_const,consts,doc)

    names = doc.createElement("names")
    parsed_names = parsed.get_names()
    add_subitems(parsed_names,names,doc)

    varnames = doc.createElement('varnames')
    parsed_varnames = parsed.get_varnames()
    add_subitems(parsed_varnames,varnames,doc)

    freevars = doc.createElement('freevars')
    parsed_freevars = parsed.get_freevars()
    add_subitems(parsed_freevars,freevars,doc)

    cellvars = doc.createElement('cellvars')
    parsed_cellvars = parsed.get_cellvars()
    add_subitems(parsed_cellvars,cellvars,doc)

    filename = doc.createElement('filename')
    parsed_filename = parsed.get_filename()
    add_subitems(parsed_filename,filename,doc)

    name = doc.createElement('name')
    parsed_name = parsed.get_names()
    add_subitems(parsed_name,name,doc)

    firstLineNo = doc.createElement('firstLineNo')
    parsed_firstLN = parsed.get_lineno()
    add_subitems(parsed_firstLN,firstLineNo,doc)

    #lnotab = doc.createElement('lnotab')
    #parsed_lnotab = parsed.get_lnotab()
    #add_subitems(parsed_lnotab,lnotab,doc)

    codeobj.appendChild(consts)
    codeobj.appendChild(names)
    codeobj.appendChild(varnames)
    codeobj.appendChild(freevars)
    codeobj.appendChild(cellvars)
    codeobj.appendChild(filename)
    codeobj.appendChild(name)
    codeobj.appendChild(firstLineNo)
    pycfile.appendChild(codeobj)
    doc.appendChild(pycfile)
    return doc.toprettyxml(indent='    ')


def add_subitems(parsed_item,parent_node,doc):
    if isinstance(parsed_item,str):
        parsed_item = [parsed_item]
    for i in parsed_item:
        if isinstance(i,int):
            sub_item = doc.createElement('int')
            sub_item.setAttribute('value',str(i))
        elif isinstance(i,str):
            tiny = i.split()
            if tiny[0] == 't':
                sub_item = doc.createElement('internStr')
                sub_item.setAttribute('index',str(intern_str.index(i)))
            else:
                sub_item = doc.createElement('Str')
            sub_item.setAttribute('length',str(len(tiny[1])))
            sub_item.setAttribute('value',tiny[1])
        elif isinstance(i,list):
            sub_item = doc.createElement('codeObject')
        else:
            sub_item = doc.createElement('NoneObject')
        parent_node.appendChild(sub_item)



if __name__ == "__main__":
    pycfile = main()
    parse_py = parse_pyc(pycfile)
    print output(parse_py)
