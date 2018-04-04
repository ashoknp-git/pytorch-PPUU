import torch
import os, json, pdb, math, numpy
from datetime import datetime
import scipy
from sklearn import decomposition
import sklearn.manifold as manifold

# Logging function
def log(fname, s):
    if not os.path.isdir(os.path.dirname(fname)):
            os.system("mkdir -p " + os.path.dirname(fname))
    f = open(fname, 'a')
    f.write(str(datetime.now()) + ': ' + s + '\n')
    f.close()


def save_movie(dirname, x, smooth=False, pytorch=True):
    os.system('mkdir -p ' + dirname)
    if pytorch:
        x = x.squeeze().permute(0, 2, 3, 1).cpu().numpy()
    for t in range(x.shape[0]):
        if smooth and t > 0:
            p = (x[t] + x[t-1])/2
        else:
            p = x[t]
        scipy.misc.imsave(dirname + '/im{:05d}.png'.format(t), p)


def grad_norm(net):
    total_norm = 0
    for p in net.parameters():
        param_norm = p.grad.data.norm(2)
        total_norm += param_norm ** 2
    total_norm = total_norm ** (1. / 2)
    return total_norm

def read_config(file_path):
    """Read JSON config."""
    json_object = json.load(open(file_path, 'r'))
    return json_object

def log_pdf(z, mu, sigma):
    a = 0.5*torch.sum(((z-mu)/sigma)**2, 1)
    b = torch.log(2*math.pi*torch.prod(sigma, 1))
    loss = a.squeeze() + b.squeeze()
    return loss

# embed Z distribution as well as some special z's (ztop) using PCA and tSNE. 
# Useful for visualizing predicted z vectors. 
def embed(Z, ztop, ndim=3):
    bsize = ztop.shape[0]
    nsamples = ztop.shape[1]
    dim = ztop.shape[2]
    ztop = ztop.reshape(bsize*nsamples, dim)
    Z_all=numpy.concatenate((ztop, Z), axis=0)

    # PCA
    Z_all_pca = decomposition.PCA(n_components=ndim).fit_transform(Z_all)
    ztop_pca = Z_all_pca[0:bsize*nsamples].reshape(bsize, nsamples, ndim)
    Z_pca = Z_all_pca[bsize*nsamples:]
    ztop_only_pca = decomposition.PCA(n_components=3).fit_transform(ztop)

    # Spectral
    Z_all_laplacian = manifold.SpectralEmbedding(n_components=ndim).fit_transform(Z_all)
    ztop_laplacian = Z_all_laplacian[0:bsize*nsamples].reshape(bsize, nsamples, ndim)
    Z_laplacian = Z_all_laplacian[bsize*nsamples:]
    ztop_only_laplacian = manifold.SpectralEmbedding(n_components=3).fit_transform(ztop)

    # Isomap
    Z_all_isomap = manifold.Isomap(n_components=ndim).fit_transform(Z_all)
    ztop_isomap = Z_all_isomap[0:bsize*nsamples].reshape(bsize, nsamples, ndim)
    Z_isomap = Z_all_isomap[bsize*nsamples:]
    ztop_only_isomap = manifold.Isomap(n_components=3).fit_transform(ztop)



    # TSNE
    '''
    Z_all_tsne = TSNE(n_components=2).fit_transform(Z_all)
    ztop_tsne = Z_all_tsne[0:bsize*nsamples].reshape(bsize, nsamples, 2)
    Z_tsne = Z_all_tsne[bsize*nsamples:]
    '''
#    Z_tsne, ztop_tsne = None, None
    return {'Z_pca': Z_pca, 'ztop_pca': ztop_pca, 
            'Z_laplacian': Z_laplacian, 'ztop_laplacian': ztop_laplacian,
            'Z_isomap': Z_isomap, 'ztop_isomap': ztop_isomap, 
            'ztop_only_pca': ztop_only_pca, 
            'ztop_only_laplacian': ztop_only_laplacian, 
            'ztop_only_isomap': ztop_only_isomap}
