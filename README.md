# Vehicle Detection
> Vehicle Detection Using Deep Learning and YOLO Algorithm.

*(Train YOLO v5 on a Custom Dataset)*

## Dataset

take or find vehicle images for create a special dataset for fine-tuning.

Train : 70%

Validition : 20%

Test : 10%

## wandb

to have mAP, loss, confusion matrix, and other metrics, sign in www.wandb.ai.

```
pip install wandb
```

## Train

fine-tuning on a pre-trained model of yolov5.

```
python train.py --img 640 --batch 16 --epochs 50 --data dataset.yaml --weights yolov5m.pt
```

## Test

after train, gives you weights of train and you should use them for test.

```
python detect.py --weights runs/train/exp12/weights/best.pt --source test_images/imtest13.JPG
```


you can also use the weight file in path 'runs/train/exp12/weights/best.pt' without the train.
this weight is the result of 128 epoch train on the following dataset.

##Dataset
```
https://drive.google.com/drive/folders/14a3ONSTQjAoTOqxwvBtb2cqR9AjOlnHz?usp=drive_link
```
