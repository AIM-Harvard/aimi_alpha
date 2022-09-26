"""
    ----------------------------------------
    AIME nnU-Net Pancreas - processing utils
    ----------------------------------------
    
    ----------------------------------------
    Author: Dennis Bontempi
    Email:  dennis_bontempi@dfci.harvard.edu
    ----------------------------------------
"""

import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
from scipy import ndimage
from tensorflow.keras.models import load_model


def model_pred(body_part, save_csv, model_dir, out_dir, df_img, img_arr, thr_img=0.5, thr_pat=0.5):
    """
    model prediction for IV contrast
    Arguments:
        body_part {str} -- 'HeadNeck' or 'Chest'
        df_img {pd.df} -- dataframe with scan and axial slice ID.
        img_arr {np.array} -- numpy array stacked with axial image slices.
        model_dir {str} -- directory for saved model.
        out_dir {str} -- directory for results output.
    Keyword arguments:
        thr_img {float} -- threshold to determine prediction class on image level.
        thr_pat {float} -- threshold to determine prediction class on patient level.
    return:
        dataframes of model predictions on image level and patient level
    """

    if body_part == 'HeadNeck':
        saved_model = 'EffNet_HeadNeck.h5'
    elif body_part == 'Chest':
        saved_model = 'EffNet_Chest.h5'

    ## load saved model
    # print(str(saved_model))
    model = load_model(os.path.join(model_dir, saved_model))
    ## prediction
    y_pred = model.predict(img_arr, batch_size=32)
    y_pred_class = [1 * (x[0] >= thr_img) for x in y_pred]

    ## save a dataframe for prediction on image level
    df_img['y_pred'] = np.around(y_pred, 3)
    df_img['y_pred_class'] = y_pred_class
    df_img_pred = df_img[['pat_id', 'img_id', 'y_pred', 'y_pred_class']]
    if save_csv:
        fn = 'image_prediction' + '.csv'
        df_img_pred.to_csv(os.path.join(out_dir, fn), index=False)
        print('Saved image prediction!')

    ## calcualte patient level prediction
    df_img_pred.drop(['img_id'], axis=1, inplace=True)
    df_mean = df_img_pred.groupby(['pat_id']).mean().reset_index()
    preds = df_mean['y_pred']
    y_pred = []
    for pred in preds:
        if pred > thr_pat:
            pred = 1
        else:
            pred = 0
        y_pred.append(pred)
    df_mean['predictions'] = y_pred
    df_mean.drop(['y_pred', 'y_pred_class'], axis=1, inplace=True)
    df_pat_pred = df_mean
    print('patient level pred:\n', df_pat_pred)
    if save_csv:
        fn = 'patient_prediction' + '.csv'
        df_pat_pred.to_csv(os.path.join(out_dir, fn))
        print('Saved patient prediction!')


def data_prepro(body_part, data_dir, img_files, new_spacing=[1, 1, 3],
                input_channel=3, norm_type='np_clip'):
    """
    data preprocrssing: respacing, registration, crop
    Arguments:
        crop_shape {np.array} -- array shape for cropping image.
        fixed_img_dir {str} -- dir for registered template iamge.
        data_dir {str} -- data dir.
        slice_range {np.array} -- slice range to extract axial slices of scans.
    Keyword arguments:
        input_channel {int} -- input channel 1 or 3.
        new_spacing {np.array} -- respacing size, default [1, 1, 3].
        norm_type {'str'} -- normalization methods for image, 'np_clip' or 'np_interp'
    return:
        df_img {pd.df} -- dataframe with image ID and patient ID.
        img_arr {np.array}  -- stacked numpy array from all slices of all scans.
    """

    if body_part == 'HeadNeck':
        crop_shape = [192, 192, 100]
        slice_range = range(17, 83)
        data_dir = os.path.join(data_dir, 'HeadNeck')
    elif body_part == 'Chest':
        crop_shape = [192, 192, 140]
        slice_range = range(50, 120)
        data_dir = os.path.join(data_dir, 'Chest')

    # choose first scan as registration template
    reg_template = img_files[0]

    # registration, respacing, cropping
    img_ids = []
    pat_ids = []
    slice_numbers = []
    arr = np.empty([0, 192, 192])
    for fn in img_files:
        pat_id = fn.split('/')[-1].split('.')[0].strip()
        print(pat_id)
        ## respacing
        img_nrrd = respacing(
            nrrd_dir=fn,
            interp_type='linear',
            new_spacing=new_spacing,
            patient_id=pat_id,
            return_type='nrrd',
            save_dir=None
        )
        ## registration
        img_reg = nrrd_reg_rigid_ref(
            img_nrrd=img_nrrd,
            fixed_img_dir=reg_template,
            patient_id=pat_id,
            save_dir=None
        )
        ## crop image from (500, 500, 116) to (180, 180, 60)
        img_crop = crop_image(
            nrrd_file=img_reg,
            patient_id=pat_id,
            crop_shape=crop_shape,
            return_type='npy',
            save_dir=None
        )

        ## choose slice range to cover body part
        if slice_range == None:
            data = img_crop
        else:
            data = img_crop[slice_range, :, :]
        ## clear signals lower than -1024
        data[data <= -1024] = -1024
        ## strip skull, skull UHI = ~700
        data[data > 700] = 0
        ## normalize UHI to 0 - 1, all signlas outside of [0, 1] will be 0;
        if norm_type == 'np_interp':
            data = np.interp(data, [-200, 200], [0, 1])
        elif norm_type == 'np_clip':
            data = np.clip(data, a_min=-200, a_max=200)
            MAX, MIN = data.max(), data.min()
            data = (data - MIN) / (MAX - MIN)
        ## stack all image arrays to one array for CNN input
        arr = np.concatenate([arr, data], 0)

        ## create image ID and slice index for img
        slice_numbers.append(data.shape[0])
        for i in range(data.shape[0]):
            img = data[i, :, :]
            img_id = pat_id + '_' + 'slice%s' % (f'{i:03d}')
            img_ids.append(img_id)
            pat_ids.append(pat_id)

    # generate patient and slice ID
    df_img = pd.DataFrame({'pat_id': pat_ids, 'img_id': img_ids})

    # covert 1 channel input to 3 channel inputs for CNN
    if input_channel == 1:
        img_arr = arr.reshape(arr.shape[0], arr.shape[1], arr.shape[2], 1)
        # print('img_arr shape:', img_arr.shape)
        # np.save(os.path.join(pro_data_dir, fn_arr_1ch), img_arr)
    elif input_channel == 3:
        img_arr = np.broadcast_to(arr, (3, arr.shape[0], arr.shape[1], arr.shape[2]))
        img_arr = np.transpose(img_arr, (1, 2, 3, 0))

    return df_img, img_arr



def nrrd_reg_rigid_ref(img_nrrd, fixed_img_dir, patient_id, save_dir):
    fixed_img = sitk.ReadImage(fixed_img_dir, sitk.sitkFloat32)
    moving_img = img_nrrd
    #    moving_img = sitk.ReadImage(img_nrrd, sitk.sitkUInt32)
    # moving_img = sitk.ReadImage(input_path, sitk.sitkFloat32)

    transform = sitk.CenteredTransformInitializer(
        fixed_img,
        moving_img,
        sitk.Euler3DTransform(),
        sitk.CenteredTransformInitializerFilter.GEOMETRY
    )

    # multi-resolution rigid registration using Mutual Information
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(sitk.sitkLinear)

    registration_method.SetOptimizerAsGradientDescent(
        learningRate=1.0,
        numberOfIterations=100,
        convergenceMinimumValue=1e-6,
        convergenceWindowSize=10
    )

    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    registration_method.SetInitialTransform(transform)
    final_transform = registration_method.Execute(fixed_img, moving_img)
    moving_img_resampled = sitk.Resample(
        moving_img,
        fixed_img,
        final_transform,
        sitk.sitkLinear,
        0.0,
        moving_img.GetPixelID()
    )
    img_reg = moving_img_resampled

    if save_dir != None:
        nrrd_fn = str(patient_id) + '.nrrd'
        sitk.WriteImage(img_reg, os.path.join(save_dir, nrrd_fn))

    return img_reg
    # return fixed_img, moving_img, final_transform


# --------------------------------------------------------------------------------------
# crop image
# -------------------------------------------------------------------------------------
def crop_image(nrrd_file, patient_id, crop_shape, return_type, save_dir):
    ## load stik and arr
    img_arr = sitk.GetArrayFromImage(nrrd_file)
    ## Return top 25 rows of 3D volume, centered in x-y space / start at anterior (y=0)?
    #    img_arr = np.transpose(img_arr, (2, 1, 0))
    #    print("image_arr shape: ", img_arr.shape)
    c, y, x = img_arr.shape
    #    x, y, c = image_arr.shape
    #    print('c:', c)
    #    print('y:', y)
    #    print('x:', x)

    ## Get center of mass to center the crop in Y plane
    mask_arr = np.copy(img_arr)
    mask_arr[mask_arr > -500] = 1
    mask_arr[mask_arr <= -500] = 0
    mask_arr[mask_arr >= -500] = 1
    # print("mask_arr min and max:", np.amin(mask_arr), np.amax(mask_arr))
    centermass = ndimage.measurements.center_of_mass(mask_arr)  # z,x,y
    cpoint = c - crop_shape[2] // 2
    # print("cpoint, ", cpoint)
    centermass = ndimage.measurements.center_of_mass(mask_arr[cpoint, :, :])
    # print("center of mass: ", centermass)
    startx = int(centermass[0] - crop_shape[0] // 2)
    starty = int(centermass[1] - crop_shape[1] // 2)
    # startx = x//2 - crop_shape[0]//2
    # starty = y//2 - crop_shape[1]//2
    startz = int(c - crop_shape[2])
    # print("start X, Y, Z: ", startx, starty, startz)

    ## crop image using crop shape
    if startz < 0:
        img_arr = np.pad(
            img_arr,
            ((abs(startz) // 2, abs(startz) // 2), (0, 0), (0, 0)),
            'constant',
            constant_values=-1024
        )
        img_crop_arr = img_arr[
                       0:crop_shape[2],
                       starty:starty + crop_shape[1],
                       startx:startx + crop_shape[0]
                       ]
    else:
        img_crop_arr = img_arr[
                       #           0:crop_shape[2],
                       startz:startz + crop_shape[2],
                       starty:starty + crop_shape[1],
                       startx:startx + crop_shape[0]
                       ]
    if img_crop_arr.shape[0] < crop_shape[2]:
        # print('initial cropped image shape too small:', img_arr.shape)
        # print(crop_shape[2], img_crop_arr.shape[0])
        img_crop_arr = np.pad(
            img_crop_arr,
            ((int(crop_shape[2] - img_crop_arr.shape[0]), 0), (0, 0), (0, 0)),
            'constant',
            constant_values=-1024
        )
        # print("padded size: ", img_crop_arr.shape)
    # print(img_crop_arr.shape)
    ## get nrrd from numpy array
    img_crop_nrrd = sitk.GetImageFromArray(img_crop_arr)
    img_crop_nrrd.SetSpacing(nrrd_file.GetSpacing())
    img_crop_nrrd.SetOrigin(nrrd_file.GetOrigin())

    if save_dir != None:
        fn = str(patient_id) + '.nrrd'
        writer = sitk.ImageFileWriter()
        writer.SetFileName(os.path.join(save_dir, fn))
        writer.SetUseCompression(True)
        writer.Execute(img_crop_nrrd)

    if return_type == 'nrrd':
        return img_crop_nrrd

    elif return_type == 'npy':
        return img_crop_arr


#--------------------------------------------------------------------------
# rescale to a common "more compact" size (either downsample or upsample)
#--------------------------------------------------------------------------
def respacing(nrrd_dir, interp_type, new_spacing, patient_id, return_type, save_dir):
    ### calculate new spacing
    img = sitk.ReadImage(nrrd_dir)
    old_size = img.GetSize()
    old_spacing = img.GetSpacing()
    # print('{} {}'.format('old size: ', old_size))
    # print('{} {}'.format('old spacing: ', old_spacing))

    new_size = [
        int(round((old_size[0] * old_spacing[0]) / float(new_spacing[0]))),
        int(round((old_size[1] * old_spacing[1]) / float(new_spacing[1]))),
        int(round((old_size[2] * old_spacing[2]) / float(new_spacing[2])))
    ]

    # print('{} {}'.format('new size: ', new_size))

    ### choose interpolation algorithm
    if interp_type == 'linear':
        interp_type = sitk.sitkLinear
    elif interp_type == 'bspline':
        interp_type = sitk.sitkBSpline
    elif interp_type == 'nearest_neighbor':
        interp_type = sitk.sitkNearestNeighbor

    ### interpolate
    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(new_spacing)
    resample.SetSize(new_size)
    resample.SetOutputOrigin(img.GetOrigin())
    resample.SetOutputDirection(img.GetDirection())
    resample.SetInterpolator(interp_type)
    resample.SetDefaultPixelValue(img.GetPixelIDValue())
    resample.SetOutputPixelType(sitk.sitkFloat32)
    img_nrrd = resample.Execute(img)

    ## save nrrd images
    if save_dir != None:
        writer = sitk.ImageFileWriter()
        writer.SetFileName(os.path.join(save_dir, '{}.nrrd'.format(patient_id)))
        writer.SetUseCompression(True)
        writer.Execute(img_nrrd)

    ## save as numpy array
    img_arr = sitk.GetArrayFromImage(img_nrrd)

    if return_type == 'nrrd':
        return img_nrrd

    elif return_type == 'npy':
        return img_arr
 