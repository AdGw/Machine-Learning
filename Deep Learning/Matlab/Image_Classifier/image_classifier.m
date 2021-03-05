%unzip('Data.zip');
imds = imageDatastore('C:\Users\Adi\Documents\Coding\Machine-Learning\Deep Learning\Python\Image_Classifier\data2','IncludeSubfolders',true,'LabelSource','foldernames');
[imdsTrain,imdsValidation] = splitEachLabel(imds,0.7,'randomized');

augimdsTrain = augmentedImageDatastore([224 224 3],imdsTrain, 'ColorPreprocessing', 'gray2rgb');
augimdsValidation = augmentedImageDatastore([224 224 3],imdsValidation, 'ColorPreprocessing', 'gray2rgb');

options = trainingOptions('adam', ...
    'MiniBatchSize',32, ...
    'MaxEpochs',10, ...
    'Shuffle','every-epoch', ...
    'InitialLearnRate',1e-4, ...
    'ValidationData',augimdsValidation, ...
    'ValidationFrequency',32, ...
    'Verbose',false, ...
    'Plots','training-progress');

netTransfer = trainNetwork(augimdsTrain,lgraph_1,options);
%%
[YPred,probs] = classify(netTransfer,augimdsValidation);
accuracy = mean(YPred == imdsValidation.Labels)

idx = randperm(numel(augimdsValidation.Files),9);
figure
for i = 1:9
    subplot(3,3,i)
    I = readimage(imdsValidation,idx(i));
    imshow(I)
    label = YPred(idx(i));
    title(string(label) + ", " + num2str(100*max(probs(idx(i),:)),3) + "%");
end
%%
I = imread("images/dowod.jpg");
inputSize = netTransfer.Layers(1).InputSize;
inputSize
I = imresize(I,inputSize(1:2));
[label,scores] = classify(netTransfer,I);
label, scores
classNames = netTransfer.Layers(end).ClassNames;
numClasses = numel(classNames);
disp(classNames(randperm(numClasses,3)))
figure
imshow(I)
title(string(label) + ", " + num2str(100*scores(classNames == label),3) + "%");
%%
filename = 'network2.onnx';
exportONNXNetwork(netTransfer,filename)