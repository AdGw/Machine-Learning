unzip('Data.zip');
imds = imageDatastore('C:\Users\Adi\Documents\Coding\Machine-Learning\Deep Learning\Matlab\Image_Classifier','IncludeSubfolders',true,'LabelSource','foldernames');
[imdsTrain,imdsValidation] = splitEachLabel(imds,0.7,'randomized');

augimdsTrain = augmentedImageDatastore([224 224],imdsTrain, 'ColorPreprocessing', 'gray2rgb');
augimdsValidation = augmentedImageDatastore([224 224],imdsValidation);

options = trainingOptions('sgdm', ...
    'MiniBatchSize',10, ...
    'MaxEpochs',6, ...
    'Shuffle','every-epoch', ...
    'InitialLearnRate',1e-4, ...
    'ValidationData',augimdsValidation, ...
    'ValidationFrequency',6, ...
    'Verbose',false, ...
    'Plots','training-progress');

netTransfer = trainNetwork(augimdsTrain,lgraph_1,options);

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
I = imread("test/x1.png");
inputSize = netTransfer.Layers(1).InputSize;
I = imresize(I,inputSize(1:2));
[label,scores] = classify(netTransfer,I);
label, scores
classNames = netTransfer.Layers(end).ClassNames;
numClasses = numel(classNames);
disp(classNames(randperm(numClasses,3)))
figure
imshow(I)
title(string(label) + ", " + num2str(100*scores(classNames == label),3) + "%");
