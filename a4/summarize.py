"""
sumarize.py
"""
def main():
    collect = open("collect_output.txt",'r').readlines()
    cluster =  open("cluster_output.txt",'r').readlines()
    classify = open("classify_output.txt",'r').readlines()
    f = open("summary.txt","w")
    f.writelines(collect)
    f.writelines(cluster)
    f.writelines(classify)
    f.close()

if __name__ == '__main__':
    main()
