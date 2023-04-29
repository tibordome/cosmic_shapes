#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 18:23:43 2021
"""

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
import os
import sys
import inspect
import numpy as np
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(currentdir, '..')) # Only needed if cosmic_profiles is not installed
from cosmic_profiles import DensShapeProfsGadget, updateInUnitSystem, updateOutUnitSystem

# Parameters
updateInUnitSystem(length_in_cm = 'Mpc/h', mass_in_g = 'Msun/h', velocity_in_cm_per_s = 1e5, little_h = 0.6774)
updateOutUnitSystem(length_in_cm = 'kpc/h', mass_in_g = 'Msun/h', velocity_in_cm_per_s = 1e5, little_h = 0.6774)
CAT_DEST = "./cat"
GROUP_DEST = "./ex_data/LLGas256b20/groups_035"
SNAP_DEST = "./ex_data/LLGas256b20/snapdir_035/snap_035"
VIZ_DEST = "./viz"
D_LOGSTART = -2.0
D_LOGEND = 0.5
D_BINS = 30 # If D_LOGSTART == -2 D_LOGEND == 1, 60 corresponds to shell width of 0.05 dex
IT_TOL = np.float32(1e-2)
IT_WALL = 100
IT_MIN = 10
SNAP = '035'
CENTER = 'mode'
MIN_NUMBER_PTCS = 200
RVIR_OR_R200 = 'R200' # Whether or not we want quantities (e.g. D_LOGSTART) expressed with respect to the virial radius Rvir or the overdensity radius R200
OBJ_TYPE = 'dm' # Which simulation particles to consider, 'dm', 'gas' or 'stars'
ROverR200 = np.logspace(-1.5,0,70)
HIST_NB_BINS = 11 # Number of bins used for e.g. ellipticity histogram
frac_r200 = 0.5 # At what depth to calculate e.g. histogram of triaxialities (cf. plotLocalTHist())

def HDF5Ex():
    
    # Define DensShapeProfsGadget object
    cprofiles = DensShapeProfsGadget(SNAP_DEST, GROUP_DEST, OBJ_TYPE, SNAP, VIZ_DEST, CAT_DEST, RVIR_OR_R200 = RVIR_OR_R200, MIN_NUMBER_PTCS = MIN_NUMBER_PTCS, D_LOGSTART = D_LOGSTART, D_LOGEND = D_LOGEND, D_BINS = D_BINS, IT_TOL = IT_TOL, IT_WALL = IT_WALL, IT_MIN = IT_MIN, CENTER = CENTER)
    
    obj_size = cprofiles.getIdxCat()[1] # Only rank == 0 content is of interest
    if rank == 0:
        h_idx_cat_len = len(obj_size)
    else:
        h_idx_cat_len = None
    h_idx_cat_len = comm.bcast(h_idx_cat_len, root = 0)
    obj_numbers = [0,1,2,3,4,5]
    
    ########################## Calculating Morphological Properties ###############################
    # Create halo shape catalogue
    cprofiles.dumpShapeCatLocal(obj_numbers, reduced = False, shell_based = False)

    # Create global halo shape catalogue
    cprofiles.dumpShapeCatGlobal(obj_numbers, reduced = False)

    ######################################## Visualizations #######################################
    # Viz first few halos' shapes
    cprofiles.vizLocalShapes(obj_numbers = obj_numbers, reduced = False, shell_based = False)
    
    # Plot halo ellipticity histogram
    cprofiles.plotGlobalEpsHist(HIST_NB_BINS, obj_numbers)

    # Plot halo triaxiality histogram
    cprofiles.plotLocalTHist(HIST_NB_BINS, frac_r200, obj_numbers, reduced = False, shell_based = False)

    # Draw halo shape profiles (overall and mass-decomposed ones)
    cprofiles.plotShapeProfs(nb_bins = 2, obj_numbers = obj_numbers, reduced = False, shell_based = False)

    ########################## Calculating and Visualizing Density Profs ##########################
    # Create local halo density catalogue
    dens_profs = cprofiles.estDensProfs(ROverR200, obj_numbers, direct_binning = True)

    if rank != 0:
        dens_profs = np.zeros((len(obj_numbers), len(ROverR200)), dtype = np.float32)
    comm.Bcast(dens_profs, root = 0)
    
    # Fit density profiles
    best_fits = cprofiles.fitDensProfs(dens_profs[:,25:], ROverR200[25:], 'nfw', obj_numbers) # Structured numpy array

    # Draw halo density profiles (overall and mass-decomposed ones). The results from getDensProfsBestFits() got cached.
    cprofiles.plotDensProfs(dens_profs, ROverR200, dens_profs[:,25:], ROverR200[25:], method = 'nfw', nb_bins = 2, obj_numbers = obj_numbers)

HDF5Ex()
