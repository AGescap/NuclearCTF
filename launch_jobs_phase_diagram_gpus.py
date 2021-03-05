####### mo #
import os
import shutil
import time
import numpy as np
import fileinput

def launching_jobs():
    
    time_s = '5-20:00:00 '
    partition = 'titan' ## 'titan' #'compute' #'compute' # 'gpu' # 
    
    if partition == 'titan':        
        gpu_type =  'titan_v'
        memoryReq = '12G' #check! '9G' #
        cpu_per_task = '1'
        
    elif partition =='tesla':
        gpu_type = 'tesla_v100-pcie-32gb' # 'titan_v'
        memoryReq = '32G' #check! '9G' #
        cpu_per_task = '1'
        
    elif partition =='compute':
        memoryReq = '2G' #check! '9G' #
        cpu_per_task = '48'
        
    node_list = 0

    ### PARAMETERS ###
    # DEFINING THE OSCILLATIONS
    stop_osc = '1'
    stop_osc_at_epoch = '600'
    start_osc_from_the_middle = '0'
    w_max_list = '1 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150'
    num_periods_list = [2910, 1763, 1077, 646, 393, 238, 144, 87, 53, 32, 19] 
    repeat_sim = '20'

    # MYRTLE Neural Net
    myrtle_depth = '5'
    myrtle_width = '64'

    #LOSS 
    loss_function_type = 'cross_entropy'

    ### DEFINING THE DATASET ###
    type_data_set = 'complete'
    
    ### TRAINING THE NN ###
    optimizer_type = 'nesterov'
    momentum_nest = '0.9'
    mini_batch_size = '512'
    weight_decay = '0.0'
    epochs_extrema_LR = '0 300 700'
    LRs_extrema = '0.0 0.02 0.002'
    steps_to_save_data = '100'
    seed_initialization = 1
    
    name = 'myrtle_phase_diagram_' + 'width_' + str(myrtle_width) + '_depth_' + str(myrtle_depth)  # +  '_amp_' + '{0:.2E}'.format(amplitude) + '_fr_' + '{0:.2E}'.format(freq) + '_sim_' +  str(it_sim+sim_shift) +'_param_ini_' + str(param_ini) +'_batchSize_' + str(batchSize) + '_NumChannels_' + str(NumChannels)  #    +'_BS_' + str(miniBatchSize) + '_net_width_' +  str(net_width) + '_convSize_' + str(convSize) + '_pools_' + str(poolSize) + '_NuCh_' + str(NumChannels)   

    name_py_script = 'myrtle_cifar10_sgd_nesterov_minibatches_piecewise_linear_lr_stop_osc_epoch_foriloop_weight_decay.py'

    folder_name = name
    os.mkdir(folder_name)
    shutil.copy(name_py_script, folder_name)
##    shutil.copy('lanczos.py',folder_name)
##    shutil.copy('hessian_computation.py',folder_name)
##    shutil.copy('density.py',folder_name)
    os.chdir(folder_name)

    for num_period in num_periods_list:

        seed_initialization = seed_initialization + 10000

        job_name = 'job_num_per_{0}.sh'.format(num_period)
        
        f = open(job_name,'w')

        f.write('#!/bin/bash\n')
        f.write('#SBATCH --job-name=ave_pha_diag   ### Job Name\n')
        f.write('#SBATCH --partition={0}      ### Quality of Service (like a queue in PBS)\n'.format(partition))                            
        f.write('#SBATCH --time={0}    ### Wall clock time limit in Days-HH:MM:SS \n'.format(time_s))                              
        f.write('#SBATCH --nodes=1             ### Node count required for the job\n ')                                     
        f.write('#SBATCH --cpus-per-task={0} \n'.format(cpu_per_task))

        if not node_list == 0:
            f.write('#SBATCH --nodelist={0} \n'.format(node_list))                            
        
        f.write('#SBATCH --ntasks=1 \n')
    
        if partition == 'titan' or partition == 'tesla':            
            f.write('#SBATCH --gres=gpu:{0}:1          ### General REServation of gpu:number of gpus \n'.format(gpu_type))
                        
        f.write('#SBATCH --mem-per-cpu={0}\n'.format(memoryReq))

        f.write('source ~/.bashrc \n')
        f.write('module load gcc/9.2.0 \n')
        f.write('module load cuda/cuda-latest \n')

        if partition == 'titan' or partition == 'tesla':
            f.write('conda activate jax_GPU \n')
        elif partition == 'compute':
            f.write('conda activate jax_env \n')

        f.write('python3 ' + name_py_script + ' --stop_osc ' + stop_osc + ' --stop_osc_at_epoch ' + stop_osc_at_epoch + ' --start_osc_from_the_middle ' + start_osc_from_the_middle + ' --w_max_list ' + w_max_list
                + ' --num_period ' + str(num_period) + ' --repeat_sim ' + repeat_sim + ' --myrtle_depth ' + myrtle_depth + ' --myrtle_width ' + myrtle_width + ' --loss_function_type ' +loss_function_type
                + ' --type_data_set ' + type_data_set + ' --optimizer_type ' +optimizer_type + ' --momentum_nest ' + momentum_nest
                + ' --weight_decay ' + weight_decay + ' --mini_batch_size ' + mini_batch_size 
                + ' --epochs_extrema_LR ' + epochs_extrema_LR + ' --LRs_extrema ' + LRs_extrema + ' --steps_to_save_data ' + steps_to_save_data
                + ' --seed_initialization ' + str(seed_initialization) )       
                
        f.close()

        time.sleep(0.1)

        os.system('sbatch ' + job_name)
##        
##        os.system('python3 ' + name_py_script  + ' --last_period_no_osc ' + last_period_no_osc + ' --start_osc_from_the_middle ' + start_osc_from_the_middle + ' --w_max_list ' + w_max_list
##        + ' --num_period ' + str(num_period) + ' --repeat_sim ' + repeat_sim + ' --myrtle_depth ' + myrtle_depth + ' --myrtle_width ' + myrtle_width + ' --loss_function_type ' +loss_function_type
##        + ' --type_data_set ' + type_data_set + ' --optimizer_type ' +optimizer_type + ' --momentum_nest ' + momentum_nest
##        + ' --weight_decay ' + weight_decay + ' --mini_batch_size ' + mini_batch_size + ' --mini_batch_size_acc ' + mini_batch_size_acc
##        + ' --epochs_for_LR ' + epochs_for_LR +' --LRs_for_phases ' + LRs_for_phases + ' --steps_to_save_data ' + steps_to_save_data
##        + ' --seed_initialization ' + str(seed_initialization) ) 
##
##        print('launching done')
        
    os.chdir('..')

launching_jobs()







