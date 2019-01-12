# Log Version 3

This is a log of all the progress made for the art recognition project.

## January 5, 2019

**Today's Progress**

1. Discussed with Ben and Michal about our objectives and plans.
  * We discussed possibilities of scraping artworks from Wikipedia or [MoMa](https://www.moma.org/collection/?fbclid=IwAR2YrXrfWNHidoUsCB86_s_C28h-_NnxOsggwxTO5WeJkHBrSbw_FR4cbak)
  * We decided that machine learning (more specifically semi-supervised deep learning with convolutional neural network) would be the best way to approach our goals.
  * However, we can also frame this problem as a unsupervised deep learning.
  * We wanted to answer questions like:  
    Do certain neighborhoods have preferences?  
    Do they favor certain types of art?  
    How are we going to categorize the art in a neighborhood?  
    How can we classify pictures we might pull from instagram into categories that we can then use to look at neighborhoods preferences for particular types of visual art? 
  * We discussed how we can compare style of images by comparing the lower layers of cnns and finding a metric to measure mathematically defined style. Like what I did [here](https://github.com/JinLi711/Neural-Style-Transfer)  
  * Discussed how we can leverage resources like the supercomputer at Midway.  

2. Found existing datasets we could use.

**Thoughts** It is important to note that me and Ben have different objectives from Michal. Whereas Michal wants to create an app of some sort to be able to recognize artworks after taking a picture, me and Ben want to analyze how distributions of artwork types vary from location to another.

**Thoughts** There probably is not a need to scrape because there are datasets out there that we can use for free.

**Things To Do** 

1. Prepare for meeting with Ben at 4:45 p.m. Monday at the Regenstein Library.
2. Find and explore resources that we can leverage. Jot notes down.

## January 6, 2019

**Today's Progress**

1. Added onto the [resources page](https://github.com/JinLi711/UIA/blob/master/Art_Recognition/Resources.md).
2. Read up on clustering algorithms.
  * Source: [Introduction To Clustering Algorithms](https://medium.freecodecamp.org/how-machines-make-sense-of-big-data-an-introduction-to-clustering-algorithms-4bd97d4fbaba)
  * K-Means Clustering. Basically randomly assign items into different categories, calculate the mean in each category, and then for each item, move that item to the category where the difference between the value of the item and the mean of that category is the lowerst. One variation of this is to randomly assign one item to one group, and then start assigning the other items to the groups. But note that we need to know the categories before hand.
  * Hierarchical Clustering. Create a distance matrix. Pair the observations with lowest distance. Repeat. End up with an heirchal structure.
  * Graph Community Detection. Skimmed it since it's not incredibly important for what we are trying to accomplish.
  * [Edge-Betweenness.](https://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm) Start with all vertices grouped in one giant cluster. Then iteratively removes least important edges, producing a hierarchal structure.
  * [Clique Percolation.](https://en.wikipedia.org/wiki/Clique_percolation_method) 
  * [Spectral clustering](https://en.wikipedia.org/wiki/Spectral_clustering)

3. Took a look at [OpenCV](https://opencv.org/). This is not used for training (we use keras or tensorflow for that) but more for analyzing the results of the training.

**Thoughts** OpenCV might not support Keras (not sure)


## January 7, 2019

**Today's Progress** 

1. Spent almost two hours talking to Ben about our objectives and plans.

2. Looked up different clustering algorithms metrics
  * [Silhouette Score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
  * [Homogeneity, completeness and V-measure](https://scikit-learn.org/stable/modules/clustering.html#homogeneity-completeness-and-v-measure)
  * [Calinski-Harabaz Index](https://scikit-learn.org/stable/modules/clustering.html#calinski-harabaz-index)  

## January 9, 2019

**Today's Progress** 

1. Spent some time discussing possible clustering algorithms and metrics.

2. Read this research [paper](https://arxiv.org/abs/1704.08614). This paper is quite relevant since it discusses using a semilabeled dataset to classify both style and mood. It also explains the BAM dataset, which might be a good alternative since it focuses on comtemporary art.

**Things To Do** 

1. Get Google Cloud started. Start training.

## January 10, 2019

**Today's Progress** 

1. Learned how to use Google Cloud and helped Ben set up Google Cloud.
  * [Using Google Datalab and BigQuery for Image Classification comparison](https://medium.com/google-cloud/using-google-datalab-and-bigquery-for-image-classification-comparison-13b2ffb26e67)
  * [Jupyter Notebook in GCP](https://towardsdatascience.com/running-jupyter-notebook-in-google-cloud-platform-in-15-min-61e16da34d52)

**Thoughts** Ben's going to talk to his father, who has access to resources that we might need. Also, I am going to work on a much smaller dataset at first simply because it would be quicker to produce results to see what goes wrong.

**Things To Do**

  * Check out this [article](https://www.analyticsvidhya.com/blog/2018/06/unsupervised-deep-learning-computer-vision/).
  * Check this out too [Image Similarity With Deep Ranking](https://medium.com/@akarshzingade/image-similarity-using-deep-ranking-c1bd83855978)

## January 11, 2019

**Today's Progress** 

1. Created a quick and dirty model for clustering.
  * I did some brief visualization (see the frequencies of each class and took a peak at the images)
  * Removed bad/ corrupted files (the dataset has corrupted files, not sure why. But I'm pretty sure the pictures have already been corrupted, and not just corrupted on my computer)
  * Wrote a brief script that extracts the style layers. Not sure what to do with this because the styles are of different tensors (since VGG19 decreases the number of dimensions as layers approach the top).

## January 12, 2019

**Today's Progress** 

1. Tried Mini-batch. This is just a base model, and not actually intended to be used. Not even sure how to interpret the results. I may have to rethink the clustering method, simply because I'm not familar with it. I've decided to take a step back and do more research. It may be smarter to replicate what already exists.

2. Looked Into Incremental PCA, very useful for online learning [source](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.IncrementalPCA.html), as I can reduce the dimensions of the images while keeping high variance.

3. Looked into many other clustering methods, but found that sklearn only supports two online learning clustering algorithms (has partial_fit). The first one is mini-batch k-means, second one is [Birch clustering method](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.Birch.html#sklearn.cluster.Birch). This method is scalable for large datasets, but not by number of features, so it would not be useful for hundreds of thousands of images.
  * Basic recap of Birch method:
  > " It constructs a tree data structure with the cluster centroids being read off the leaf." 

4. Checked out feature extraction from [sklearn](https://scikit-learn.org/0.15/modules/feature_extraction.html#feature-extraction). Most important thing to look at is the image feature extraction at the very end. Patch extraction may end up being useful, and graph connectivity for image segmentation may end up being used.

**Things To Do** 

1. Check out [Restricted Boltzmann Machine](https://skymind.ai/wiki/restricted-boltzmann-machine) and Deep Belief networks. Low priority since these are outdated methods. 
  * [Sklearn](https://scikit-learn.org/stable/modules/neural_networks_unsupervised.html) implementation.
