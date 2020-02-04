"""
Softmax loss.
"""

import tensorflow as tf


def compute_softmax_loss(scores, labels, group_size):
    """
    It computes the sum of negative log softmax loss:
    -sum_i lables_i * log(exp(scores_i) / (exp(scores_1) + ... + exp(scores_n)))
    """
    # mask the padded documents
    mask = tf.sequence_mask(group_size, maxlen=tf.shape(scores)[1], dtype=tf.float32)
    # softmax loss
    loss = mask * labels * (-scores + tf.expand_dims(compute_logsumexp_mask(scores, mask), axis=1))
    return loss


def compute_sigmoid_cross_entropy_loss(scores, labels, group_size):
    """ Compute loss for pointwise ranking

    :param scores: Tensor  Shape=[batch_size, max_group_size]
    :param labels: Tensor  Shape=[batch_size, max_group_size]
    :param group_size: Tensor  Shape=[batch_size]
    :return: Tensor  Shape=[batch_size, max_group_size]
   """
    mask = tf.sequence_mask(group_size, maxlen=tf.shape(scores)[1], dtype=tf.float32)
    loss = mask * tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=scores)
    return tf.reduce_sum(loss, axis=-1)


def compute_logsumexp_mask(scores, mask):
    """
    Compute logsumexp with mask for a batch.
    Current tf.lossumexp does not support mask.
    """
    # Change padding scores to be the score of the first element in the score array. I.e., if
    #   original_scores = [[1., -1., PAD_SCORE], [2., -2., PAD_SCORE]], result_scores will be
    #   [[1., -1., 1.], [2., -2., 2]]. This is to make sure the maximum value is chosen from
    #   VALID scores
    scores = tf.where(tf.cast(mask, dtype=tf.bool), scores,
                      tf.ones_like(scores) * tf.expand_dims(scores[:, 0], axis=-1))
    max_scores = tf.reduce_max(scores, axis=-1, keepdims=True)
    scores = scores - max_scores
    exp_score_withmask = tf.exp(scores) * tf.cast(mask, dtype=tf.float32)
    logsumexp = tf.math.log(tf.reduce_sum(exp_score_withmask, axis=-1)) + tf.squeeze(max_scores, -1)
    return logsumexp
