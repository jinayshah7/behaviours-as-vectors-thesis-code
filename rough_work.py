from sklearn.model_selection import KFold

data = range(20,30)
target = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

second_data = [(d, t+5) for d, t in zip(data, target)]
print(second_data)
kfold = KFold(4)
# enumerate splits
for d in kfold.split(data):
    print(d)
