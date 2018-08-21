url = sys.argv[1]
data = requests.get(url).text
with open(sys.argv[2], 'w') as f:
    f.write(data)