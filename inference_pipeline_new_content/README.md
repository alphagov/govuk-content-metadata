## Compute instance scaling

You can specify a single instance (or node) to process your batch prediction request. This tutorial uses a single node, so the variables MIN_NODES and MAX_NODES are both set to 1.

If you want to use multiple nodes to process your batch prediction request, set MAX_NODES to the maximum number of nodes you want to use. Vertex AI autoscales the number of nodes used to serve your predictions, up to the maximum number you set. Refer to the pricing page to understand the costs of autoscaling with multiple nodes

Ref:
- https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/custom/sdk-custom-image-classification-batch.ipynb
- https://cloud.google.com/vertex-ai/pricing#pred_eur
- https://cloud.google.com/vertex-ai/pricing#custom-trained_models
- https://cloud.google.com/vertex-ai/docs/predictions/configure-compute
