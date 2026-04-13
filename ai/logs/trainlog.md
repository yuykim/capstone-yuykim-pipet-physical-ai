# 26.04.07 

(base) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot
export PYTHONPATH="/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src:$PYTHONPATH"
(lerobot) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ python -m lerobot.scripts.lerobot_train \
  --dataset.repo_id pipet_dataset \
  --dataset.root /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/training_data_360_idle_v3 \
  --policy.type act \
  --policy.push_to_hub false \
  --policy.device cuda \
  --output_dir /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle \
  --job_name act_360_idle_10k \
  --batch_size 8 \
  --steps 10000 \
  --eval_freq 5000 \
  --policy.chunk_size 40 \
  --policy.n_action_steps 40 \
  --policy.use_vae false \
  --policy.use_amp true \
  --dataset.use_imagenet_stats true \
  2>&1 | tee /tmp/act_360_idle_10k.log
INFO 2026-04-07 16:50:53 ot_train.py:197 {'batch_size': 8,
 'checkpoint_path': None,
 'cudnn_deterministic': False,
 'dataset': {'episodes': None,
             'image_transforms': {'enable': False,
                                  'max_num_transforms': 3,
                                  'random_order': False,
                                  'tfs': {'affine': {'kwargs': {'degrees': [-5.0,
                                                                            5.0],
                                                                'translate': [0.05,
                                                                              0.05]},
                                                     'type': 'RandomAffine',
                                                     'weight': 1.0},
                                          'brightness': {'kwargs': {'brightness': [0.8,
                                                                                   1.2]},
                                                         'type': 'ColorJitter',
                                                         'weight': 1.0},
                                          'contrast': {'kwargs': {'contrast': [0.8,
                                                                               1.2]},
                                                       'type': 'ColorJitter',
                                                       'weight': 1.0},
                                          'hue': {'kwargs': {'hue': [-0.05,
                                                                     0.05]},
                                                  'type': 'ColorJitter',
                                                  'weight': 1.0},
                                          'saturation': {'kwargs': {'saturation': [0.5,
                                                                                   1.5]},
                                                         'type': 'ColorJitter',
                                                         'weight': 1.0},
                                          'sharpness': {'kwargs': {'sharpness': [0.5,
                                                                                 1.5]},
                                                        'type': 'SharpnessJitter',
                                                        'weight': 1.0}}},
             'repo_id': 'pipet_dataset',
             'revision': None,
             'root': '/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/training_data_360_idle_v3',
             'streaming': False,
             'use_imagenet_stats': True,
             'video_backend': 'torchcodec'},
 'env': None,
 'eval': {'batch_size': 50, 'n_episodes': 50, 'use_async_envs': False},
 'eval_freq': 5000,
 'job_name': 'act_360_idle_10k',
 'log_freq': 200,
 'num_workers': 4,
 'optimizer': {'betas': [0.9, 0.999],
               'eps': 1e-08,
               'grad_clip_norm': 10.0,
               'lr': 1e-05,
               'type': 'adamw',
               'weight_decay': 0.0001},
 'output_dir': '/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle',
 'peft': None,
 'policy': {'chunk_size': 40,
            'device': 'cuda',
            'dim_feedforward': 3200,
            'dim_model': 512,
            'dropout': 0.1,
            'feedforward_activation': 'relu',
            'input_features': {},
            'kl_weight': 10.0,
            'latent_dim': 32,
            'license': None,
            'n_action_steps': 40,
            'n_decoder_layers': 1,
            'n_encoder_layers': 4,
            'n_heads': 8,
            'n_obs_steps': 1,
            'n_vae_encoder_layers': 4,
            'normalization_mapping': {'ACTION': <NormalizationMode.MEAN_STD: 'MEAN_STD'>,
                                      'STATE': <NormalizationMode.MEAN_STD: 'MEAN_STD'>,
                                      'VISUAL': <NormalizationMode.MEAN_STD: 'MEAN_STD'>},
            'optimizer_lr': 1e-05,
            'optimizer_lr_backbone': 1e-05,
            'optimizer_weight_decay': 0.0001,
            'output_features': {},
            'pre_norm': False,
            'pretrained_backbone_weights': 'ResNet18_Weights.IMAGENET1K_V1',
            'pretrained_path': None,
            'private': None,
            'push_to_hub': False,
            'replace_final_stride_with_dilation': False,
            'repo_id': None,
            'tags': None,
            'temporal_ensemble_coeff': None,
            'type': 'act',
            'use_amp': True,
            'use_peft': False,
            'use_vae': False,
            'vision_backbone': 'resnet18'},
 'rabc_epsilon': 1e-06,
 'rabc_head_mode': 'sparse',
 'rabc_kappa': 0.01,
 'rabc_progress_path': None,
 'rename_map': {},
 'resume': False,
 'save_checkpoint': True,
 'save_freq': 20000,
 'scheduler': None,
 'seed': 1000,
 'steps': 10000,
 'tolerance_s': 0.0001,
 'use_policy_training_preset': True,
 'use_rabc': False,
 'wandb': {'add_tags': True,
           'disable_artifact': False,
           'enable': False,
           'entity': None,
           'mode': None,
           'notes': None,
           'project': 'lerobot',
           'run_id': None}}
INFO 2026-04-07 16:50:53 ot_train.py:205 Logs will be saved locally.
INFO 2026-04-07 16:50:53 ot_train.py:221 Creating dataset
INFO 2026-04-07 16:50:53 eo_utils.py:108 Using video codec: libsvtav1
INFO 2026-04-07 16:50:56 ot_train.py:239 Creating policy
INFO 2026-04-07 16:50:56 ot_train.py:294 Creating optimizer and scheduler
INFO 2026-04-07 16:50:56 ot_train.py:329 Output dir: /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle
INFO 2026-04-07 16:50:56 ot_train.py:336 cfg.steps=10000 (10K)
INFO 2026-04-07 16:50:56 ot_train.py:337 dataset.num_frames=3335 (3K)
INFO 2026-04-07 16:50:56 ot_train.py:338 dataset.num_episodes=4
INFO 2026-04-07 16:50:56 ot_train.py:341 Effective batch size: 8 x 1 = 8
INFO 2026-04-07 16:50:56 ot_train.py:342 num_learnable_params=34199879 (34M)
INFO 2026-04-07 16:50:56 ot_train.py:343 num_total_params=34199879 (34M)
Training:   0%|          | 0/10000 [00:00<?, ?step/s]INFO 2026-04-07 16:50:56 ot_train.py:407 Start offline training on a fixed dataset, with effective batch size: 8
Training:   2%|▏         | 200/10000 [03:27<2:01:15,  1.35step/s]INFO 2026-04-07 16:54:24 ot_train.py:439 step:200 smpl:2K ep:2 epch:0.48 loss:0.531 grdn:28.703 lr:1.0e-05 updt_s:0.130 data_s:0.908
Training:   4%|▍         | 400/10000 [06:52<1:34:58,  1.68step/s]INFO 2026-04-07 16:57:49 ot_train.py:439 step:400 smpl:3K ep:4 epch:0.96 loss:0.465 grdn:22.729 lr:1.0e-05 updt_s:0.123 data_s:0.901
Training:   6%|▌         | 600/10000 [09:54<2:35:49,  1.01step/s]INFO 2026-04-07 17:00:51 ot_train.py:439 step:600 smpl:5K ep:6 epch:1.44 loss:0.434 grdn:17.808 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:   8%|▊         | 800/10000 [12:49<2:21:50,  1.08step/s]INFO 2026-04-07 17:03:46 ot_train.py:439 step:800 smpl:6K ep:8 epch:1.92 loss:0.413 grdn:15.247 lr:1.0e-05 updt_s:0.122 data_s:0.753
Training:  10%|█         | 1000/10000 [15:51<2:24:07,  1.04step/s]INFO 2026-04-07 17:06:48 ot_train.py:439 step:1K smpl:8K ep:10 epch:2.40 loss:0.400 grdn:12.816 lr:1.0e-05 updt_s:0.121 data_s:0.790
Training:  12%|█▏        | 1200/10000 [18:50<2:00:28,  1.22step/s]INFO 2026-04-07 17:09:47 ot_train.py:439 step:1K smpl:10K ep:12 epch:2.88 loss:0.398 grdn:11.118 lr:1.0e-05 updt_s:0.120 data_s:0.774
Training:  14%|█▍        | 1400/10000 [21:55<2:14:37,  1.06step/s]INFO 2026-04-07 17:12:52 ot_train.py:439 step:1K smpl:11K ep:13 epch:3.36 loss:0.383 grdn:10.329 lr:1.0e-05 updt_s:0.121 data_s:0.798
Training:  16%|█▌        | 1600/10000 [24:56<1:56:20,  1.20step/s]INFO 2026-04-07 17:15:53 ot_train.py:439 step:2K smpl:13K ep:15 epch:3.84 loss:0.390 grdn:9.770 lr:1.0e-05 updt_s:0.122 data_s:0.785
Training:  18%|█▊        | 1800/10000 [28:02<2:56:44,  1.29s/step]INFO 2026-04-07 17:18:59 ot_train.py:439 step:2K smpl:14K ep:17 epch:4.32 loss:0.379 grdn:8.981 lr:1.0e-05 updt_s:0.122 data_s:0.806
Training:  20%|██        | 2000/10000 [31:03<2:44:04,  1.23s/step]INFO 2026-04-07 17:22:00 ot_train.py:439 step:2K smpl:16K ep:19 epch:4.80 loss:0.375 grdn:7.929 lr:1.0e-05 updt_s:0.122 data_s:0.783
Training:  22%|██▏       | 2200/10000 [34:04<2:50:01,  1.31s/step]INFO 2026-04-07 17:25:01 ot_train.py:439 step:2K smpl:18K ep:21 epch:5.28 loss:0.370 grdn:8.012 lr:1.0e-05 updt_s:0.121 data_s:0.784
Training:  24%|██▍       | 2400/10000 [37:03<2:52:44,  1.36s/step]INFO 2026-04-07 17:28:00 ot_train.py:439 step:2K smpl:19K ep:23 epch:5.76 loss:0.363 grdn:7.832 lr:1.0e-05 updt_s:0.122 data_s:0.770
Training:  26%|██▌       | 2600/10000 [40:04<1:31:19,  1.35step/s]INFO 2026-04-07 17:31:01 ot_train.py:439 step:3K smpl:21K ep:25 epch:6.24 loss:0.357 grdn:7.785 lr:1.0e-05 updt_s:0.122 data_s:0.783
Training:  28%|██▊       | 2800/10000 [43:05<1:28:27,  1.36step/s]INFO 2026-04-07 17:34:02 ot_train.py:439 step:3K smpl:22K ep:27 epch:6.72 loss:0.346 grdn:7.737 lr:1.0e-05 updt_s:0.122 data_s:0.785
Training:  30%|███       | 3000/10000 [46:09<2:40:25,  1.38s/step]INFO 2026-04-07 17:37:06 ot_train.py:439 step:3K smpl:24K ep:29 epch:7.20 loss:0.343 grdn:7.829 lr:1.0e-05 updt_s:0.123 data_s:0.795
Training:  32%|███▏      | 3200/10000 [49:11<2:39:33,  1.41s/step]INFO 2026-04-07 17:40:08 ot_train.py:439 step:3K smpl:26K ep:31 epch:7.68 loss:0.334 grdn:6.768 lr:1.0e-05 updt_s:0.122 data_s:0.787
Training:  34%|███▍      | 3400/10000 [52:13<2:06:59,  1.15s/step]INFO 2026-04-07 17:43:10 ot_train.py:439 step:3K smpl:27K ep:33 epch:8.16 loss:0.331 grdn:7.741 lr:1.0e-05 updt_s:0.122 data_s:0.788
Training:  36%|███▌      | 3600/10000 [55:13<1:02:03,  1.72step/s]INFO 2026-04-07 17:46:10 ot_train.py:439 step:4K smpl:29K ep:35 epch:8.64 loss:0.327 grdn:7.863 lr:1.0e-05 updt_s:0.122 data_s:0.780
Training:  38%|███▊      | 3800/10000 [58:16<54:32,  1.89step/s]  INFO 2026-04-07 17:49:13 ot_train.py:439 step:4K smpl:30K ep:36 epch:9.12 loss:0.319 grdn:7.840 lr:1.0e-05 updt_s:0.121 data_s:0.790
Training:  40%|████      | 4000/10000 [1:01:14<53:17,  1.88step/s]  INFO 2026-04-07 17:52:11 ot_train.py:439 step:4K smpl:32K ep:38 epch:9.60 loss:0.316 grdn:7.988 lr:1.0e-05 updt_s:0.122 data_s:0.768
Training:  42%|████▏     | 4200/10000 [1:04:15<1:40:31,  1.04s/step]INFO 2026-04-07 17:55:12 ot_train.py:439 step:4K smpl:34K ep:40 epch:10.07 loss:0.317 grdn:7.774 lr:1.0e-05 updt_s:0.122 data_s:0.783
Training:  44%|████▍     | 4400/10000 [1:07:18<2:05:08,  1.34s/step]INFO 2026-04-07 17:58:14 ot_train.py:439 step:4K smpl:35K ep:42 epch:10.55 loss:0.304 grdn:6.954 lr:1.0e-05 updt_s:0.121 data_s:0.791
Training:  46%|████▌     | 4600/10000 [1:10:17<1:21:08,  1.11step/s]INFO 2026-04-07 18:01:14 ot_train.py:439 step:5K smpl:37K ep:44 epch:11.03 loss:0.307 grdn:7.535 lr:1.0e-05 updt_s:0.122 data_s:0.775
Training:  48%|████▊     | 4800/10000 [1:13:17<47:45,  1.81step/s]  INFO 2026-04-07 18:04:14 ot_train.py:439 step:5K smpl:38K ep:46 epch:11.51 loss:0.301 grdn:6.968 lr:1.0e-05 updt_s:0.122 data_s:0.777
Training:  50%|█████     | 5000/10000 [1:16:24<44:14,  1.88step/s]INFO 2026-04-07 18:07:21 ot_train.py:439 step:5K smpl:40K ep:48 epch:11.99 loss:0.299 grdn:6.745 lr:1.0e-05 updt_s:0.123 data_s:0.813
Training:  52%|█████▏    | 5200/10000 [1:19:31<43:07,  1.86step/s]INFO 2026-04-07 18:10:28 ot_train.py:439 step:5K smpl:42K ep:50 epch:12.47 loss:0.295 grdn:6.601 lr:1.0e-05 updt_s:0.123 data_s:0.814
Training:  54%|█████▍    | 5400/10000 [1:22:38<41:27,  1.85step/s]INFO 2026-04-07 18:13:35 ot_train.py:439 step:5K smpl:43K ep:52 epch:12.95 loss:0.295 grdn:7.377 lr:1.0e-05 updt_s:0.122 data_s:0.811
Training:  56%|█████▌    | 5600/10000 [1:25:46<1:23:13,  1.13s/step]INFO 2026-04-07 18:16:43 ot_train.py:439 step:6K smpl:45K ep:54 epch:13.43 loss:0.286 grdn:6.591 lr:1.0e-05 updt_s:0.122 data_s:0.817
Training:  58%|█████▊    | 5800/10000 [1:29:09<1:13:20,  1.05s/step]INFO 2026-04-07 18:20:06 ot_train.py:439 step:6K smpl:46K ep:56 epch:13.91 loss:0.291 grdn:7.193 lr:1.0e-05 updt_s:0.124 data_s:0.888
Training:  60%|██████    | 6000/10000 [1:32:25<1:16:34,  1.15s/step]INFO 2026-04-07 18:23:22 ot_train.py:439 step:6K smpl:48K ep:58 epch:14.39 loss:0.282 grdn:7.486 lr:1.0e-05 updt_s:0.122 data_s:0.859
Training:  62%|██████▏   | 6200/10000 [1:35:39<35:23,  1.79step/s]INFO 2026-04-07 18:26:36 ot_train.py:439 step:6K smpl:50K ep:59 epch:14.87 loss:0.289 grdn:6.666 lr:1.0e-05 updt_s:0.122 data_s:0.845
Training:  64%|██████▍   | 6400/10000 [1:39:01<1:10:02,  1.17s/step]INFO 2026-04-07 18:29:58 ot_train.py:439 step:6K smpl:51K ep:61 epch:15.35 loss:0.280 grdn:6.603 lr:1.0e-05 updt_s:0.124 data_s:0.887
Training:  66%|██████▌   | 6600/10000 [1:42:12<41:23,  1.37step/s]INFO 2026-04-07 18:33:09 ot_train.py:439 step:7K smpl:53K ep:63 epch:15.83 loss:0.277 grdn:6.634 lr:1.0e-05 updt_s:0.122 data_s:0.831
Training:  68%|██████▊   | 6800/10000 [1:45:16<39:16,  1.36step/s]INFO 2026-04-07 18:36:13 ot_train.py:439 step:7K smpl:54K ep:65 epch:16.31 loss:0.280 grdn:6.965 lr:1.0e-05 updt_s:0.121 data_s:0.799
Training:  70%|███████   | 7000/10000 [1:48:17<35:22,  1.41step/s]INFO 2026-04-07 18:39:14 ot_train.py:439 step:7K smpl:56K ep:67 epch:16.79 loss:0.273 grdn:6.347 lr:1.0e-05 updt_s:0.121 data_s:0.781
Training:  72%|███████▏  | 7200/10000 [1:51:20<37:00,  1.26step/s]INFO 2026-04-07 18:42:17 ot_train.py:439 step:7K smpl:58K ep:69 epch:17.27 loss:0.275 grdn:6.046 lr:1.0e-05 updt_s:0.121 data_s:0.793
Training:  74%|███████▍  | 7400/10000 [1:54:23<57:47,  1.33s/step]INFO 2026-04-07 18:45:20 ot_train.py:439 step:7K smpl:59K ep:71 epch:17.75 loss:0.269 grdn:6.834 lr:1.0e-05 updt_s:0.121 data_s:0.796
Training:  76%|███████▌  | 7600/10000 [1:57:33<29:22,  1.36step/s]INFO 2026-04-07 18:48:30 ot_train.py:439 step:8K smpl:61K ep:73 epch:18.23 loss:0.273 grdn:6.601 lr:1.0e-05 updt_s:0.123 data_s:0.823
Training:  78%|███████▊  | 7800/10000 [2:00:37<42:41,  1.16s/step]INFO 2026-04-07 18:51:34 ot_train.py:439 step:8K smpl:62K ep:75 epch:18.71 loss:0.265 grdn:6.740 lr:1.0e-05 updt_s:0.122 data_s:0.799
Training:  80%|████████  | 8000/10000 [2:03:41<33:58,  1.02s/step]INFO 2026-04-07 18:54:38 ot_train.py:439 step:8K smpl:64K ep:77 epch:19.19 loss:0.264 grdn:6.425 lr:1.0e-05 updt_s:0.121 data_s:0.801
Training:  82%|████████▏ | 8200/10000 [2:06:44<28:52,  1.04step/s]INFO 2026-04-07 18:57:41 ot_train.py:439 step:8K smpl:66K ep:79 epch:19.67 loss:0.266 grdn:6.564 lr:1.0e-05 updt_s:0.122 data_s:0.793
Training:  84%|████████▍ | 8400/10000 [2:09:50<31:55,  1.20s/step]INFO 2026-04-07 19:00:47 ot_train.py:439 step:8K smpl:67K ep:81 epch:20.15 loss:0.265 grdn:6.424 lr:1.0e-05 updt_s:0.122 data_s:0.807
Training:  86%|████████▌ | 8600/10000 [2:12:53<23:34,  1.01s/step]INFO 2026-04-07 19:03:50 ot_train.py:439 step:9K smpl:69K ep:83 epch:20.63 loss:0.261 grdn:5.817 lr:1.0e-05 updt_s:0.122 data_s:0.789
Training:  88%|████████▊ | 8800/10000 [2:15:55<11:01,  1.81step/s]INFO 2026-04-07 19:06:52 ot_train.py:439 step:9K smpl:70K ep:84 epch:21.11 loss:0.257 grdn:6.017 lr:1.0e-05 updt_s:0.123 data_s:0.790
Training:  90%|█████████ | 9000/10000 [2:18:58<09:26,  1.76step/s]INFO 2026-04-07 19:09:55 ot_train.py:439 step:9K smpl:72K ep:86 epch:21.59 loss:0.260 grdn:6.543 lr:1.0e-05 updt_s:0.122 data_s:0.790
Training:  92%|█████████▏| 9200/10000 [2:22:01<09:46,  1.37step/s]INFO 2026-04-07 19:12:58 ot_train.py:439 step:9K smpl:74K ep:88 epch:22.07 loss:0.254 grdn:6.224 lr:1.0e-05 updt_s:0.122 data_s:0.795
Training:  94%|█████████▍| 9400/10000 [2:25:06<13:21,  1.34s/step]INFO 2026-04-07 19:16:03 ot_train.py:439 step:9K smpl:75K ep:90 epch:22.55 loss:0.254 grdn:5.679 lr:1.0e-05 updt_s:0.122 data_s:0.801
Training:  96%|█████████▌| 9600/10000 [2:28:09<07:08,  1.07s/step]INFO 2026-04-07 19:19:06 ot_train.py:439 step:10K smpl:77K ep:92 epch:23.03 loss:0.254 grdn:5.937 lr:1.0e-05 updt_s:0.122 data_s:0.791
Training:  98%|█████████▊| 9800/10000 [2:31:11<03:13,  1.03step/s]INFO 2026-04-07 19:22:08 ot_train.py:439 step:10K smpl:78K ep:94 epch:23.51 loss:0.255 grdn:6.123 lr:1.0e-05 updt_s:0.122 data_s:0.790
Training: 100%|██████████| 10000/10000 [2:34:13<00:00,  1.13s/step]INFO 2026-04-07 19:25:10 ot_train.py:439 step:10K smpl:80K ep:96 epch:23.99 loss:0.246 grdn:5.372 lr:1.0e-05 updt_s:0.122 data_s:0.788
INFO 2026-04-07 19:25:10 ot_train.py:459 Checkpoint policy after step 10000
Training: 100%|██████████| 10000/10000 [2:34:14<00:00,  1.08step/s]
INFO 2026-04-07 19:25:11 ot_train.py:533 End of training
(lerobot) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ python -m lerobot.scripts.lerobot_train \
  --dataset.repo_id pipet_dataset \
  --dataset.root /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/training_data_360_idle_v3 \
  --policy.type act \
  --policy.push_to_hub false \
  --policy.device cuda \
  --output_dir /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle \
  --job_name act_360_idle_10k \
  --resume true \
  --batch_size 8 \
  --steps 30000 \
  --eval_freq 5000 \
  --log_freq 20 \
  --policy.chunk_size 40 \
  --policy.n_action_steps 40 \
  --policy.use_vae false \
  --policy.use_amp true \
  --dataset.use_imagenet_stats true \
  2>&1 | tee /tmp/act_360_idle_30k_resume.log
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/scripts/lerobot_train.py", line 555, in <module>
    main()
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/scripts/lerobot_train.py", line 551, in main
    train()
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/configs/parser.py", line 233, in wrapper_inner
    response = fn(cfg, *args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/scripts/lerobot_train.py", line 170, in train
    cfg.validate()
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/configs/train.py", line 96, in validate
    raise ValueError(
ValueError: A config_path is expected when resuming a run. Please specify path to train_config.json
(lerobot) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ export PYTHONPATH="/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src:$PYTHONPATH"
python -m lerobot.scripts.lerobot_train \
  --dataset.repo_id pipet_dataset \
  --dataset.root /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/training_data_360_idle_v3 \
  --policy.type act \
  --policy.push_to_hub false \
  --policy.device cuda \
  --output_dir /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle \
  --job_name act_360_idle_10k \
  --resume true \
  --batch_size 8 \
  --steps 30000 \
  --eval_freq 5000 \
  --log_freq 20 \
  --policy.chunk_size 40 \
  --policy.n_action_steps 40 \
  --policy.use_vae false \
  --policy.use_amp true \
  --dataset.use_imagenet_stats true \
  2>&1 | tee /tmp/act_360_idle_30k_resume.log
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/scripts/lerobot_train.py", line 555, in <module>
    main()
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/scripts/lerobot_train.py", line 551, in main
    train()
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/configs/parser.py", line 233, in wrapper_inner
    response = fn(cfg, *args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/scripts/lerobot_train.py", line 170, in train
    cfg.validate()
  File "/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src/lerobot/configs/train.py", line 96, in validate
    raise ValueError(
ValueError: A config_path is expected when resuming a run. Please specify path to train_config.json
(lerobot) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
(lerobot) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot
export PYTHONPATH="/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src:$PYTHONPATH"

python -m lerobot.scripts.lerobot_train \
  --config_path=/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle/checkpoints/010000/pretrained_model/train_config.json \
  --resume true \
  --dataset.root /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/training_data_360_idle_v3 \
  --steps 30000 \
  --eval_freq 5000 \
  --log_freq 20 \
  2>&1 | tee /tmp/act_360_idle_30k_resume.log
INFO 2026-04-07 19:36:11 ot_train.py:197 {'batch_size': 8,
 'checkpoint_path': '/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle/checkpoints/010000',
 'cudnn_deterministic': False,
 'dataset': {'episodes': None,
             'image_transforms': {'enable': False,
                                  'max_num_transforms': 3,
                                  'random_order': False,
                                  'tfs': {'affine': {'kwargs': {'degrees': [-5.0,
                                                                            5.0],
                                                                'translate': [0.05,
                                                                              0.05]},
                                                     'type': 'RandomAffine',
                                                     'weight': 1.0},
                                          'brightness': {'kwargs': {'brightness': [0.8,
                                                                                   1.2]},
                                                         'type': 'ColorJitter',
                                                         'weight': 1.0},
                                          'contrast': {'kwargs': {'contrast': [0.8,
                                                                               1.2]},
                                                       'type': 'ColorJitter',
                                                       'weight': 1.0},
                                          'hue': {'kwargs': {'hue': [-0.05,
                                                                     0.05]},
                                                  'type': 'ColorJitter',
                                                  'weight': 1.0},
                                          'saturation': {'kwargs': {'saturation': [0.5,
                                                                                   1.5]},
                                                         'type': 'ColorJitter',
                                                         'weight': 1.0},
                                          'sharpness': {'kwargs': {'sharpness': [0.5,
                                                                                 1.5]},
                                                        'type': 'SharpnessJitter',
                                                        'weight': 1.0}}},
             'repo_id': 'pipet_dataset',
             'revision': None,
             'root': '/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/training_data_360_idle_v3',
             'streaming': False,
             'use_imagenet_stats': True,
             'video_backend': 'torchcodec'},
 'env': None,
 'eval': {'batch_size': 50, 'n_episodes': 50, 'use_async_envs': False},
 'eval_freq': 5000,
 'job_name': 'act_360_idle_10k',
 'log_freq': 20,
 'num_workers': 4,
 'optimizer': {'betas': [0.9, 0.999],
               'eps': 1e-08,
               'grad_clip_norm': 10.0,
               'lr': 1e-05,
               'type': 'adamw',
               'weight_decay': 0.0001},
 'output_dir': '/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle',
 'peft': None,
 'policy': {'chunk_size': 40,
            'device': 'cuda',
            'dim_feedforward': 3200,
            'dim_model': 512,
            'dropout': 0.1,
            'feedforward_activation': 'relu',
            'input_features': {'observation.images.front': {'shape': [3,
                                                                      360,
                                                                      480],
                                                            'type': <FeatureType.VISUAL: 'VISUAL'>},
                               'observation.images.overhead': {'shape': [3,
                                                                         360,
                                                                         480],
                                                               'type': <FeatureType.VISUAL: 'VISUAL'>},
                               'observation.state': {'shape': [18],
                                                     'type': <FeatureType.STATE: 'STATE'>}},
            'kl_weight': 10.0,
            'latent_dim': 32,
            'license': None,
            'n_action_steps': 40,
            'n_decoder_layers': 1,
            'n_encoder_layers': 4,
            'n_heads': 8,
            'n_obs_steps': 1,
            'n_vae_encoder_layers': 4,
            'normalization_mapping': {'ACTION': <NormalizationMode.MEAN_STD: 'MEAN_STD'>,
                                      'STATE': <NormalizationMode.MEAN_STD: 'MEAN_STD'>,
                                      'VISUAL': <NormalizationMode.MEAN_STD: 'MEAN_STD'>},
            'optimizer_lr': 1e-05,
            'optimizer_lr_backbone': 1e-05,
            'optimizer_weight_decay': 0.0001,
            'output_features': {'action': {'shape': [7],
                                           'type': <FeatureType.ACTION: 'ACTION'>}},
            'pre_norm': False,
            'pretrained_backbone_weights': 'ResNet18_Weights.IMAGENET1K_V1',
            'pretrained_path': '/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle/checkpoints/010000/pretrained_model',
            'private': None,
            'push_to_hub': False,
            'replace_final_stride_with_dilation': 0,
            'repo_id': None,
            'tags': None,
            'temporal_ensemble_coeff': None,
            'type': 'act',
            'use_amp': True,
            'use_peft': False,
            'use_vae': False,
            'vision_backbone': 'resnet18'},
 'rabc_epsilon': 1e-06,
 'rabc_head_mode': 'sparse',
 'rabc_kappa': 0.01,
 'rabc_progress_path': None,
 'rename_map': {},
 'resume': True,
 'save_checkpoint': True,
 'save_freq': 20000,
 'scheduler': None,
 'seed': 1000,
 'steps': 30000,
 'tolerance_s': 0.0001,
 'use_policy_training_preset': True,
 'use_rabc': False,
 'wandb': {'add_tags': True,
           'disable_artifact': False,
           'enable': False,
           'entity': None,
           'mode': None,
           'notes': None,
           'project': 'lerobot',
           'run_id': None}}
INFO 2026-04-07 19:36:11 ot_train.py:205 Logs will be saved locally.
INFO 2026-04-07 19:36:11 ot_train.py:221 Creating dataset
INFO 2026-04-07 19:36:12 eo_utils.py:108 Using video codec: libsvtav1
INFO 2026-04-07 19:36:12 ot_train.py:239 Creating policy
INFO 2026-04-07 19:36:12 ot_train.py:294 Creating optimizer and scheduler
INFO 2026-04-07 19:36:12 ot_train.py:329 Output dir: /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act_360_idle
INFO 2026-04-07 19:36:12 ot_train.py:336 cfg.steps=30000 (30K)
INFO 2026-04-07 19:36:12 ot_train.py:337 dataset.num_frames=3335 (3K)
INFO 2026-04-07 19:36:12 ot_train.py:338 dataset.num_episodes=4
INFO 2026-04-07 19:36:12 ot_train.py:341 Effective batch size: 8 x 1 = 8
INFO 2026-04-07 19:36:12 ot_train.py:342 num_learnable_params=34199879 (34M)
INFO 2026-04-07 19:36:12 ot_train.py:343 num_total_params=34199879 (34M)
Loading weights from local directory
Training:   0%|          | 0/20000 [00:00<?, ?step/s]INFO 2026-04-07 19:36:12 ot_train.py:407 Start offline training on a fixed dataset, with effective batch size: 8
Training:   0%|          | 20/20000 [00:21<6:50:05,  1.23s/step]INFO 2026-04-07 19:36:34 ot_train.py:439 step:10K smpl:80K ep:96 epch:24.04 loss:0.251 grdn:6.006 lr:1.0e-05 updt_s:0.179 data_s:0.894
Training:   0%|          | 40/20000 [00:38<6:56:56,  1.25s/step]INFO 2026-04-07 19:36:51 ot_train.py:439 step:10K smpl:80K ep:96 epch:24.08 loss:0.246 grdn:6.126 lr:1.0e-05 updt_s:0.125 data_s:0.748
Training:   0%|          | 60/20000 [00:56<6:55:43,  1.25s/step]INFO 2026-04-07 19:37:09 ot_train.py:439 step:10K smpl:80K ep:97 epch:24.13 loss:0.246 grdn:5.997 lr:1.0e-05 updt_s:0.124 data_s:0.760
Training:   0%|          | 80/20000 [01:13<6:37:20,  1.20s/step]INFO 2026-04-07 19:37:26 ot_train.py:439 step:10K smpl:81K ep:97 epch:24.18 loss:0.251 grdn:5.807 lr:1.0e-05 updt_s:0.125 data_s:0.736
Training:   0%|          | 100/20000 [01:31<6:16:51,  1.14s/step]INFO 2026-04-07 19:37:43 ot_train.py:439 step:10K smpl:81K ep:97 epch:24.23 loss:0.258 grdn:6.226 lr:1.0e-05 updt_s:0.123 data_s:0.739
Training:   1%|          | 120/20000 [01:49<6:09:09,  1.11s/step]INFO 2026-04-07 19:38:01 ot_train.py:439 step:10K smpl:81K ep:97 epch:24.28 loss:0.257 grdn:6.107 lr:1.0e-05 updt_s:0.124 data_s:0.773
Training:   1%|          | 140/20000 [02:06<5:58:58,  1.08s/step]INFO 2026-04-07 19:38:19 ot_train.py:439 step:10K smpl:81K ep:97 epch:24.32 loss:0.236 grdn:5.487 lr:1.0e-05 updt_s:0.124 data_s:0.770
Training:   1%|          | 160/20000 [02:24<5:34:26,  1.01s/step]INFO 2026-04-07 19:38:37 ot_train.py:439 step:10K smpl:81K ep:97 epch:24.37 loss:0.241 grdn:6.777 lr:1.0e-05 updt_s:0.122 data_s:0.749
Training:   1%|          | 180/20000 [02:42<5:44:26,  1.04s/step]INFO 2026-04-07 19:38:54 ot_train.py:439 step:10K smpl:81K ep:98 epch:24.42 loss:0.245 grdn:4.820 lr:1.0e-05 updt_s:0.122 data_s:0.762
Training:   1%|          | 200/20000 [03:00<5:29:05,  1.00step/s]INFO 2026-04-07 19:39:12 ot_train.py:439 step:10K smpl:82K ep:98 epch:24.47 loss:0.245 grdn:5.175 lr:1.0e-05 updt_s:0.122 data_s:0.789
Training:   1%|          | 220/20000 [03:18<5:52:33,  1.07s/step]INFO 2026-04-07 19:39:30 ot_train.py:439 step:10K smpl:82K ep:98 epch:24.52 loss:0.251 grdn:5.658 lr:1.0e-05 updt_s:0.122 data_s:0.772
Training:   1%|          | 240/20000 [03:36<6:49:36,  1.24s/step]INFO 2026-04-07 19:39:49 ot_train.py:439 step:10K smpl:82K ep:98 epch:24.56 loss:0.253 grdn:6.178 lr:1.0e-05 updt_s:0.123 data_s:0.803
Training:   1%|▏         | 260/20000 [03:54<6:19:40,  1.15s/step]INFO 2026-04-07 19:40:07 ot_train.py:439 step:10K smpl:82K ep:98 epch:24.61 loss:0.256 grdn:6.149 lr:1.0e-05 updt_s:0.123 data_s:0.758
Training:   1%|▏         | 280/20000 [04:12<6:03:52,  1.11s/step]INFO 2026-04-07 19:40:24 ot_train.py:439 step:10K smpl:82K ep:99 epch:24.66 loss:0.239 grdn:5.605 lr:1.0e-05 updt_s:0.123 data_s:0.773
Training:   2%|▏         | 300/20000 [04:29<5:24:08,  1.01step/s]INFO 2026-04-07 19:40:42 ot_train.py:439 step:10K smpl:82K ep:99 epch:24.71 loss:0.242 grdn:5.891 lr:1.0e-05 updt_s:0.123 data_s:0.757
Training:   2%|▏         | 320/20000 [04:47<4:54:14,  1.11step/s]INFO 2026-04-07 19:41:00 ot_train.py:439 step:10K smpl:83K ep:99 epch:24.76 loss:0.243 grdn:5.772 lr:1.0e-05 updt_s:0.123 data_s:0.756
Training:   2%|▏         | 340/20000 [05:04<4:43:33,  1.16step/s]INFO 2026-04-07 19:41:17 ot_train.py:439 step:10K smpl:83K ep:99 epch:24.80 loss:0.252 grdn:6.225 lr:1.0e-05 updt_s:0.124 data_s:0.748
Training:   2%|▏         | 360/20000 [05:22<4:46:57,  1.14step/s]INFO 2026-04-07 19:41:35 ot_train.py:439 step:10K smpl:83K ep:99 epch:24.85 loss:0.253 grdn:6.139 lr:1.0e-05 updt_s:0.123 data_s:0.761
Training:   2%|▏         | 380/20000 [05:40<4:52:12,  1.12step/s]INFO 2026-04-07 19:41:53 ot_train.py:439 step:10K smpl:83K ep:100 epch:24.90 loss:0.245 grdn:5.751 lr:1.0e-05 updt_s:0.124 data_s:0.785
Training:   2%|▏         | 400/20000 [05:58<4:33:32,  1.19step/s]INFO 2026-04-07 19:42:10 ot_train.py:439 step:10K smpl:83K ep:100 epch:24.95 loss:0.241 grdn:5.698 lr:1.0e-05 updt_s:0.124 data_s:0.742
Training:   2%|▏         | 420/20000 [06:16<4:59:59,  1.09step/s]INFO 2026-04-07 19:42:28 ot_train.py:439 step:10K smpl:83K ep:100 epch:25.00 loss:0.249 grdn:5.812 lr:1.0e-05 updt_s:0.148 data_s:0.760
Training:   2%|▏         | 440/20000 [06:35<3:06:52,  1.74step/s]INFO 2026-04-07 19:42:47 ot_train.py:439 step:10K smpl:84K ep:100 epch:25.04 loss:0.238 grdn:5.792 lr:1.0e-05 updt_s:0.125 data_s:0.810
Training:   2%|▏         | 460/20000 [06:53<3:05:09,  1.76step/s]INFO 2026-04-07 19:43:06 ot_train.py:439 step:10K smpl:84K ep:100 epch:25.09 loss:0.238 grdn:5.871 lr:1.0e-05 updt_s:0.138 data_s:0.806
Training:   2%|▏         | 480/20000 [07:12<3:02:51,  1.78step/s]INFO 2026-04-07 19:43:24 ot_train.py:439 step:10K smpl:84K ep:101 epch:25.14 loss:0.248 grdn:5.911 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:   2%|▎         | 500/20000 [07:29<2:57:38,  1.83step/s]INFO 2026-04-07 19:43:42 ot_train.py:439 step:10K smpl:84K ep:101 epch:25.19 loss:0.242 grdn:7.180 lr:1.0e-05 updt_s:0.124 data_s:0.763
Training:   3%|▎         | 520/20000 [07:48<3:02:32,  1.78step/s]INFO 2026-04-07 19:44:01 ot_train.py:439 step:11K smpl:84K ep:101 epch:25.24 loss:0.251 grdn:6.497 lr:1.0e-05 updt_s:0.124 data_s:0.821
Training:   3%|▎         | 540/20000 [08:06<2:58:17,  1.82step/s]INFO 2026-04-07 19:44:19 ot_train.py:439 step:11K smpl:84K ep:101 epch:25.28 loss:0.256 grdn:6.187 lr:1.0e-05 updt_s:0.124 data_s:0.780
Training:   3%|▎         | 560/20000 [08:24<2:51:50,  1.89step/s]INFO 2026-04-07 19:44:37 ot_train.py:439 step:11K smpl:84K ep:101 epch:25.33 loss:0.245 grdn:5.316 lr:1.0e-05 updt_s:0.124 data_s:0.767
Training:   3%|▎         | 580/20000 [08:42<2:52:47,  1.87step/s]INFO 2026-04-07 19:44:55 ot_train.py:439 step:11K smpl:85K ep:102 epch:25.38 loss:0.249 grdn:6.458 lr:1.0e-05 updt_s:0.124 data_s:0.771
Training:   3%|▎         | 600/20000 [09:00<3:00:52,  1.79step/s]INFO 2026-04-07 19:45:13 ot_train.py:439 step:11K smpl:85K ep:102 epch:25.43 loss:0.247 grdn:5.114 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:   3%|▎         | 620/20000 [09:19<3:08:14,  1.72step/s]INFO 2026-04-07 19:45:31 ot_train.py:439 step:11K smpl:85K ep:102 epch:25.48 loss:0.241 grdn:5.800 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:   3%|▎         | 640/20000 [09:37<2:52:21,  1.87step/s]INFO 2026-04-07 19:45:50 ot_train.py:439 step:11K smpl:85K ep:102 epch:25.52 loss:0.242 grdn:5.280 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:   3%|▎         | 660/20000 [09:55<3:01:47,  1.77step/s]INFO 2026-04-07 19:46:08 ot_train.py:439 step:11K smpl:85K ep:102 epch:25.57 loss:0.247 grdn:6.946 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:   3%|▎         | 680/20000 [10:14<3:04:09,  1.75step/s]INFO 2026-04-07 19:46:27 ot_train.py:439 step:11K smpl:85K ep:102 epch:25.62 loss:0.253 grdn:7.775 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:   4%|▎         | 700/20000 [10:32<2:57:47,  1.81step/s]INFO 2026-04-07 19:46:45 ot_train.py:439 step:11K smpl:86K ep:103 epch:25.67 loss:0.243 grdn:6.873 lr:1.0e-05 updt_s:0.126 data_s:0.788
Training:   4%|▎         | 720/20000 [10:50<2:52:24,  1.86step/s]INFO 2026-04-07 19:47:03 ot_train.py:439 step:11K smpl:86K ep:103 epch:25.72 loss:0.244 grdn:6.374 lr:1.0e-05 updt_s:0.125 data_s:0.768
Training:   4%|▎         | 740/20000 [11:08<2:52:47,  1.86step/s]INFO 2026-04-07 19:47:21 ot_train.py:439 step:11K smpl:86K ep:103 epch:25.76 loss:0.253 grdn:6.456 lr:1.0e-05 updt_s:0.125 data_s:0.783
Training:   4%|▍         | 760/20000 [11:27<3:02:25,  1.76step/s]INFO 2026-04-07 19:47:39 ot_train.py:439 step:11K smpl:86K ep:103 epch:25.81 loss:0.253 grdn:7.104 lr:1.0e-05 updt_s:0.124 data_s:0.788
Training:   4%|▍         | 780/20000 [11:45<2:58:39,  1.79step/s]INFO 2026-04-07 19:47:58 ot_train.py:439 step:11K smpl:86K ep:103 epch:25.86 loss:0.243 grdn:5.860 lr:1.0e-05 updt_s:0.125 data_s:0.810
Training:   4%|▍         | 800/20000 [12:03<2:55:55,  1.82step/s]INFO 2026-04-07 19:48:16 ot_train.py:439 step:11K smpl:86K ep:104 epch:25.91 loss:0.248 grdn:5.217 lr:1.0e-05 updt_s:0.125 data_s:0.787
Training:   4%|▍         | 820/20000 [12:22<2:54:35,  1.83step/s]INFO 2026-04-07 19:48:34 ot_train.py:439 step:11K smpl:87K ep:104 epch:25.96 loss:0.243 grdn:6.197 lr:1.0e-05 updt_s:0.126 data_s:0.788
Training:   4%|▍         | 840/20000 [12:43<4:59:23,  1.07step/s]INFO 2026-04-07 19:48:56 ot_train.py:439 step:11K smpl:87K ep:104 epch:26.00 loss:0.246 grdn:6.382 lr:1.0e-05 updt_s:0.124 data_s:0.948
Training:   4%|▍         | 860/20000 [13:02<4:17:36,  1.24step/s]INFO 2026-04-07 19:49:15 ot_train.py:439 step:11K smpl:87K ep:104 epch:26.05 loss:0.240 grdn:6.348 lr:1.0e-05 updt_s:0.125 data_s:0.807
Training:   4%|▍         | 880/20000 [13:21<4:35:04,  1.16step/s]INFO 2026-04-07 19:49:34 ot_train.py:439 step:11K smpl:87K ep:104 epch:26.10 loss:0.237 grdn:4.802 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:   4%|▍         | 900/20000 [13:39<4:04:58,  1.30step/s]INFO 2026-04-07 19:49:52 ot_train.py:439 step:11K smpl:87K ep:105 epch:26.15 loss:0.248 grdn:5.192 lr:1.0e-05 updt_s:0.123 data_s:0.788
Training:   5%|▍         | 920/20000 [13:58<4:03:30,  1.31step/s]INFO 2026-04-07 19:50:10 ot_train.py:439 step:11K smpl:87K ep:105 epch:26.19 loss:0.246 grdn:5.561 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:   5%|▍         | 940/20000 [14:16<4:08:47,  1.28step/s]INFO 2026-04-07 19:50:29 ot_train.py:439 step:11K smpl:88K ep:105 epch:26.24 loss:0.241 grdn:5.718 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:   5%|▍         | 960/20000 [14:35<4:11:13,  1.26step/s]INFO 2026-04-07 19:50:48 ot_train.py:439 step:11K smpl:88K ep:105 epch:26.29 loss:0.244 grdn:6.445 lr:1.0e-05 updt_s:0.123 data_s:0.817
Training:   5%|▍         | 980/20000 [14:54<4:18:11,  1.23step/s]INFO 2026-04-07 19:51:06 ot_train.py:439 step:11K smpl:88K ep:105 epch:26.34 loss:0.233 grdn:4.732 lr:1.0e-05 updt_s:0.123 data_s:0.821
Training:   5%|▌         | 1000/20000 [15:13<4:21:09,  1.21step/s]INFO 2026-04-07 19:51:25 ot_train.py:439 step:11K smpl:88K ep:106 epch:26.39 loss:0.244 grdn:5.563 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:   5%|▌         | 1020/20000 [15:31<4:08:15,  1.27step/s]INFO 2026-04-07 19:51:43 ot_train.py:439 step:11K smpl:88K ep:106 epch:26.43 loss:0.249 grdn:5.469 lr:1.0e-05 updt_s:0.125 data_s:0.778
Training:   5%|▌         | 1040/20000 [15:49<4:00:55,  1.31step/s]INFO 2026-04-07 19:52:02 ot_train.py:439 step:11K smpl:88K ep:106 epch:26.48 loss:0.241 grdn:5.934 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:   5%|▌         | 1060/20000 [16:08<3:58:44,  1.32step/s]INFO 2026-04-07 19:52:20 ot_train.py:439 step:11K smpl:88K ep:106 epch:26.53 loss:0.245 grdn:6.643 lr:1.0e-05 updt_s:0.125 data_s:0.803
Training:   5%|▌         | 1080/20000 [16:27<4:02:46,  1.30step/s]INFO 2026-04-07 19:52:39 ot_train.py:439 step:11K smpl:89K ep:106 epch:26.58 loss:0.247 grdn:6.280 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:   6%|▌         | 1100/20000 [16:46<3:59:13,  1.32step/s]INFO 2026-04-07 19:52:58 ot_train.py:439 step:11K smpl:89K ep:107 epch:26.63 loss:0.251 grdn:5.230 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:   6%|▌         | 1120/20000 [17:04<3:52:30,  1.35step/s]INFO 2026-04-07 19:53:17 ot_train.py:439 step:11K smpl:89K ep:107 epch:26.67 loss:0.239 grdn:5.054 lr:1.0e-05 updt_s:0.123 data_s:0.809
Training:   6%|▌         | 1140/20000 [17:23<4:05:00,  1.28step/s]INFO 2026-04-07 19:53:36 ot_train.py:439 step:11K smpl:89K ep:107 epch:26.72 loss:0.240 grdn:5.649 lr:1.0e-05 updt_s:0.124 data_s:0.835
Training:   6%|▌         | 1160/20000 [17:42<3:51:58,  1.35step/s]INFO 2026-04-07 19:53:55 ot_train.py:439 step:11K smpl:89K ep:107 epch:26.77 loss:0.242 grdn:5.224 lr:1.0e-05 updt_s:0.126 data_s:0.809
Training:   6%|▌         | 1180/20000 [18:00<3:49:38,  1.37step/s]INFO 2026-04-07 19:54:13 ot_train.py:439 step:11K smpl:89K ep:107 epch:26.82 loss:0.246 grdn:5.798 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:   6%|▌         | 1200/20000 [18:18<3:43:26,  1.40step/s]INFO 2026-04-07 19:54:31 ot_train.py:439 step:11K smpl:90K ep:107 epch:26.87 loss:0.242 grdn:5.296 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:   6%|▌         | 1220/20000 [18:37<3:47:16,  1.38step/s]INFO 2026-04-07 19:54:49 ot_train.py:439 step:11K smpl:90K ep:108 epch:26.91 loss:0.234 grdn:5.766 lr:1.0e-05 updt_s:0.123 data_s:0.789
Training:   6%|▌         | 1240/20000 [18:55<4:02:00,  1.29step/s]INFO 2026-04-07 19:55:08 ot_train.py:439 step:11K smpl:90K ep:108 epch:26.96 loss:0.238 grdn:5.019 lr:1.0e-05 updt_s:0.123 data_s:0.805
Training:   6%|▋         | 1260/20000 [19:17<5:47:11,  1.11s/step]INFO 2026-04-07 19:55:30 ot_train.py:439 step:11K smpl:90K ep:108 epch:27.01 loss:0.247 grdn:5.600 lr:1.0e-05 updt_s:0.123 data_s:0.962
Training:   6%|▋         | 1280/20000 [19:36<5:12:24,  1.00s/step]INFO 2026-04-07 19:55:48 ot_train.py:439 step:11K smpl:90K ep:108 epch:27.06 loss:0.241 grdn:4.792 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:   6%|▋         | 1300/20000 [19:54<5:17:42,  1.02s/step]INFO 2026-04-07 19:56:07 ot_train.py:439 step:11K smpl:90K ep:108 epch:27.11 loss:0.248 grdn:5.380 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:   7%|▋         | 1320/20000 [20:13<5:17:14,  1.02s/step]INFO 2026-04-07 19:56:25 ot_train.py:439 step:11K smpl:91K ep:109 epch:27.15 loss:0.244 grdn:5.429 lr:1.0e-05 updt_s:0.124 data_s:0.815
Training:   7%|▋         | 1340/20000 [20:31<5:06:37,  1.01step/s]INFO 2026-04-07 19:56:43 ot_train.py:439 step:11K smpl:91K ep:109 epch:27.20 loss:0.239 grdn:5.935 lr:1.0e-05 updt_s:0.124 data_s:0.769
Training:   7%|▋         | 1360/20000 [20:49<5:18:21,  1.02s/step]INFO 2026-04-07 19:57:02 ot_train.py:439 step:11K smpl:91K ep:109 epch:27.25 loss:0.234 grdn:6.038 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:   7%|▋         | 1380/20000 [21:08<5:23:24,  1.04s/step]INFO 2026-04-07 19:57:20 ot_train.py:439 step:11K smpl:91K ep:109 epch:27.30 loss:0.227 grdn:5.040 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:   7%|▋         | 1400/20000 [21:26<5:12:04,  1.01s/step]INFO 2026-04-07 19:57:39 ot_train.py:439 step:11K smpl:91K ep:109 epch:27.35 loss:0.243 grdn:5.943 lr:1.0e-05 updt_s:0.124 data_s:0.797
Training:   7%|▋         | 1420/20000 [21:44<5:05:28,  1.01step/s]INFO 2026-04-07 19:57:57 ot_train.py:439 step:11K smpl:91K ep:110 epch:27.39 loss:0.239 grdn:6.026 lr:1.0e-05 updt_s:0.125 data_s:0.770
Training:   7%|▋         | 1440/20000 [22:02<4:57:08,  1.04step/s]INFO 2026-04-07 19:58:14 ot_train.py:439 step:11K smpl:92K ep:110 epch:27.44 loss:0.239 grdn:5.637 lr:1.0e-05 updt_s:0.126 data_s:0.758
Training:   7%|▋         | 1460/20000 [22:19<4:55:54,  1.04step/s]INFO 2026-04-07 19:58:32 ot_train.py:439 step:11K smpl:92K ep:110 epch:27.49 loss:0.243 grdn:5.679 lr:1.0e-05 updt_s:0.124 data_s:0.757
Training:   7%|▋         | 1480/20000 [22:37<5:01:22,  1.02step/s]INFO 2026-04-07 19:58:50 ot_train.py:439 step:11K smpl:92K ep:110 epch:27.54 loss:0.242 grdn:6.085 lr:1.0e-05 updt_s:0.126 data_s:0.758
Training:   8%|▊         | 1500/20000 [22:55<4:51:43,  1.06step/s]INFO 2026-04-07 19:59:08 ot_train.py:439 step:12K smpl:92K ep:110 epch:27.59 loss:0.238 grdn:5.978 lr:1.0e-05 updt_s:0.125 data_s:0.765
Training:   8%|▊         | 1520/20000 [23:13<5:03:41,  1.01step/s]INFO 2026-04-07 19:59:26 ot_train.py:439 step:12K smpl:92K ep:111 epch:27.63 loss:0.239 grdn:6.006 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:   8%|▊         | 1540/20000 [23:31<4:50:52,  1.06step/s]INFO 2026-04-07 19:59:43 ot_train.py:439 step:12K smpl:92K ep:111 epch:27.68 loss:0.246 grdn:5.486 lr:1.0e-05 updt_s:0.125 data_s:0.753
Training:   8%|▊         | 1560/20000 [23:48<4:53:27,  1.05step/s]INFO 2026-04-07 20:00:01 ot_train.py:439 step:12K smpl:92K ep:111 epch:27.73 loss:0.237 grdn:5.668 lr:1.0e-05 updt_s:0.125 data_s:0.757
Training:   8%|▊         | 1580/20000 [24:06<5:09:29,  1.01s/step]INFO 2026-04-07 20:00:19 ot_train.py:439 step:12K smpl:93K ep:111 epch:27.78 loss:0.235 grdn:5.631 lr:1.0e-05 updt_s:0.125 data_s:0.784
Training:   8%|▊         | 1600/20000 [24:25<5:03:00,  1.01step/s]INFO 2026-04-07 20:00:37 ot_train.py:439 step:12K smpl:93K ep:111 epch:27.83 loss:0.245 grdn:5.513 lr:1.0e-05 updt_s:0.125 data_s:0.778
Training:   8%|▊         | 1620/20000 [24:43<5:08:45,  1.01s/step]INFO 2026-04-07 20:00:55 ot_train.py:439 step:12K smpl:93K ep:111 epch:27.87 loss:0.246 grdn:5.133 lr:1.0e-05 updt_s:0.125 data_s:0.780
Training:   8%|▊         | 1640/20000 [25:01<5:05:06,  1.00step/s]INFO 2026-04-07 20:01:14 ot_train.py:439 step:12K smpl:93K ep:112 epch:27.92 loss:0.242 grdn:4.680 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:   8%|▊         | 1660/20000 [25:19<4:52:16,  1.05step/s]INFO 2026-04-07 20:01:32 ot_train.py:439 step:12K smpl:93K ep:112 epch:27.97 loss:0.232 grdn:5.206 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:   8%|▊         | 1680/20000 [25:41<7:16:23,  1.43s/step]INFO 2026-04-07 20:01:53 ot_train.py:439 step:12K smpl:93K ep:112 epch:28.02 loss:0.242 grdn:6.457 lr:1.0e-05 updt_s:0.125 data_s:0.948
Training:   8%|▊         | 1700/20000 [26:00<7:40:57,  1.51s/step]INFO 2026-04-07 20:02:13 ot_train.py:439 step:12K smpl:94K ep:112 epch:28.07 loss:0.232 grdn:5.111 lr:1.0e-05 updt_s:0.125 data_s:0.842
Training:   9%|▊         | 1720/20000 [26:19<7:11:13,  1.42s/step]INFO 2026-04-07 20:02:32 ot_train.py:439 step:12K smpl:94K ep:112 epch:28.11 loss:0.235 grdn:4.863 lr:1.0e-05 updt_s:0.125 data_s:0.819
Training:   9%|▊         | 1740/20000 [26:37<6:50:43,  1.35s/step]INFO 2026-04-07 20:02:49 ot_train.py:439 step:12K smpl:94K ep:113 epch:28.16 loss:0.235 grdn:5.667 lr:1.0e-05 updt_s:0.133 data_s:0.762
Training:   9%|▉         | 1760/20000 [26:55<6:48:01,  1.34s/step]INFO 2026-04-07 20:03:07 ot_train.py:439 step:12K smpl:94K ep:113 epch:28.21 loss:0.237 grdn:5.728 lr:1.0e-05 updt_s:0.125 data_s:0.773
Training:   9%|▉         | 1780/20000 [27:14<7:13:40,  1.43s/step]INFO 2026-04-07 20:03:27 ot_train.py:439 step:12K smpl:94K ep:113 epch:28.26 loss:0.237 grdn:5.277 lr:1.0e-05 updt_s:0.125 data_s:0.835
Training:   9%|▉         | 1800/20000 [27:32<6:57:43,  1.38s/step]INFO 2026-04-07 20:03:45 ot_train.py:439 step:12K smpl:94K ep:113 epch:28.31 loss:0.244 grdn:5.450 lr:1.0e-05 updt_s:0.125 data_s:0.774
Training:   9%|▉         | 1820/20000 [27:50<6:12:48,  1.23s/step]INFO 2026-04-07 20:04:03 ot_train.py:439 step:12K smpl:95K ep:113 epch:28.35 loss:0.239 grdn:5.049 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:   9%|▉         | 1840/20000 [28:09<5:27:59,  1.08s/step]INFO 2026-04-07 20:04:21 ot_train.py:439 step:12K smpl:95K ep:114 epch:28.40 loss:0.240 grdn:4.798 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:   9%|▉         | 1860/20000 [28:27<4:19:50,  1.16step/s]INFO 2026-04-07 20:04:39 ot_train.py:439 step:12K smpl:95K ep:114 epch:28.45 loss:0.242 grdn:5.518 lr:1.0e-05 updt_s:0.123 data_s:0.766
Training:   9%|▉         | 1880/20000 [28:45<3:45:37,  1.34step/s]INFO 2026-04-07 20:04:58 ot_train.py:439 step:12K smpl:95K ep:114 epch:28.50 loss:0.229 grdn:5.190 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  10%|▉         | 1900/20000 [29:03<3:37:47,  1.39step/s]INFO 2026-04-07 20:05:16 ot_train.py:439 step:12K smpl:95K ep:114 epch:28.55 loss:0.239 grdn:5.560 lr:1.0e-05 updt_s:0.125 data_s:0.793
Training:  10%|▉         | 1920/20000 [29:22<3:48:49,  1.32step/s]INFO 2026-04-07 20:05:34 ot_train.py:439 step:12K smpl:95K ep:114 epch:28.59 loss:0.237 grdn:6.129 lr:1.0e-05 updt_s:0.125 data_s:0.802
Training:  10%|▉         | 1940/20000 [29:41<3:50:31,  1.31step/s]INFO 2026-04-07 20:05:53 ot_train.py:439 step:12K smpl:96K ep:115 epch:28.64 loss:0.242 grdn:6.077 lr:1.0e-05 updt_s:0.124 data_s:0.825
Training:  10%|▉         | 1960/20000 [30:00<3:46:57,  1.32step/s]INFO 2026-04-07 20:06:12 ot_train.py:439 step:12K smpl:96K ep:115 epch:28.69 loss:0.236 grdn:5.423 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  10%|▉         | 1980/20000 [30:18<3:44:57,  1.34step/s]INFO 2026-04-07 20:06:31 ot_train.py:439 step:12K smpl:96K ep:115 epch:28.74 loss:0.234 grdn:5.886 lr:1.0e-05 updt_s:0.123 data_s:0.816
Training:  10%|█         | 2000/20000 [30:37<3:41:18,  1.36step/s]INFO 2026-04-07 20:06:50 ot_train.py:439 step:12K smpl:96K ep:115 epch:28.79 loss:0.233 grdn:5.824 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  10%|█         | 2020/20000 [30:56<3:50:11,  1.30step/s]INFO 2026-04-07 20:07:08 ot_train.py:439 step:12K smpl:96K ep:115 epch:28.83 loss:0.238 grdn:6.116 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  10%|█         | 2040/20000 [31:14<3:45:56,  1.32step/s]INFO 2026-04-07 20:07:27 ot_train.py:439 step:12K smpl:96K ep:116 epch:28.88 loss:0.243 grdn:4.900 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  10%|█         | 2060/20000 [31:33<3:47:47,  1.31step/s]INFO 2026-04-07 20:07:46 ot_train.py:439 step:12K smpl:96K ep:116 epch:28.93 loss:0.237 grdn:5.004 lr:1.0e-05 updt_s:0.125 data_s:0.831
Training:  10%|█         | 2080/20000 [31:53<3:44:02,  1.33step/s]INFO 2026-04-07 20:08:05 ot_train.py:439 step:12K smpl:97K ep:116 epch:28.98 loss:0.241 grdn:5.957 lr:1.0e-05 updt_s:0.123 data_s:0.840
Training:  10%|█         | 2100/20000 [32:12<2:56:23,  1.69step/s]INFO 2026-04-07 20:08:25 ot_train.py:439 step:12K smpl:97K ep:116 epch:29.03 loss:0.238 grdn:5.395 lr:1.0e-05 updt_s:0.123 data_s:0.847
Training:  11%|█         | 2120/20000 [32:31<3:01:19,  1.64step/s]INFO 2026-04-07 20:08:44 ot_train.py:439 step:12K smpl:97K ep:116 epch:29.07 loss:0.236 grdn:5.911 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:  11%|█         | 2140/20000 [32:50<3:05:15,  1.61step/s]INFO 2026-04-07 20:09:03 ot_train.py:439 step:12K smpl:97K ep:116 epch:29.12 loss:0.237 grdn:5.715 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  11%|█         | 2160/20000 [33:09<3:03:09,  1.62step/s]INFO 2026-04-07 20:09:22 ot_train.py:439 step:12K smpl:97K ep:117 epch:29.17 loss:0.234 grdn:5.098 lr:1.0e-05 updt_s:0.123 data_s:0.814
Training:  11%|█         | 2180/20000 [33:28<3:18:07,  1.50step/s]INFO 2026-04-07 20:09:41 ot_train.py:439 step:12K smpl:97K ep:117 epch:29.22 loss:0.238 grdn:6.147 lr:1.0e-05 updt_s:0.124 data_s:0.847
Training:  11%|█         | 2200/20000 [33:47<3:13:28,  1.53step/s]INFO 2026-04-07 20:10:00 ot_train.py:439 step:12K smpl:98K ep:117 epch:29.27 loss:0.240 grdn:5.488 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  11%|█         | 2220/20000 [34:06<3:02:15,  1.63step/s]INFO 2026-04-07 20:10:19 ot_train.py:439 step:12K smpl:98K ep:117 epch:29.31 loss:0.232 grdn:5.188 lr:1.0e-05 updt_s:0.125 data_s:0.812
Training:  11%|█         | 2240/20000 [34:24<2:47:56,  1.76step/s]INFO 2026-04-07 20:10:37 ot_train.py:439 step:12K smpl:98K ep:117 epch:29.36 loss:0.226 grdn:5.148 lr:1.0e-05 updt_s:0.124 data_s:0.774
Training:  11%|█▏        | 2260/20000 [34:43<3:03:09,  1.61step/s]INFO 2026-04-07 20:10:56 ot_train.py:439 step:12K smpl:98K ep:118 epch:29.41 loss:0.241 grdn:5.179 lr:1.0e-05 updt_s:0.123 data_s:0.823
Training:  11%|█▏        | 2280/20000 [35:02<3:11:26,  1.54step/s]INFO 2026-04-07 20:11:15 ot_train.py:439 step:12K smpl:98K ep:118 epch:29.46 loss:0.248 grdn:6.119 lr:1.0e-05 updt_s:0.123 data_s:0.829
Training:  12%|█▏        | 2300/20000 [35:21<3:23:27,  1.45step/s]INFO 2026-04-07 20:11:34 ot_train.py:439 step:12K smpl:98K ep:118 epch:29.51 loss:0.236 grdn:4.914 lr:1.0e-05 updt_s:0.123 data_s:0.834
Training:  12%|█▏        | 2320/20000 [35:40<3:24:15,  1.44step/s]INFO 2026-04-07 20:11:52 ot_train.py:439 step:12K smpl:99K ep:118 epch:29.55 loss:0.235 grdn:5.094 lr:1.0e-05 updt_s:0.123 data_s:0.815
Training:  12%|█▏        | 2340/20000 [35:59<3:37:55,  1.35step/s]INFO 2026-04-07 20:12:12 ot_train.py:439 step:12K smpl:99K ep:118 epch:29.60 loss:0.233 grdn:5.807 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  12%|█▏        | 2360/20000 [36:18<3:44:30,  1.31step/s]INFO 2026-04-07 20:12:31 ot_train.py:439 step:12K smpl:99K ep:119 epch:29.65 loss:0.236 grdn:5.084 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  12%|█▏        | 2380/20000 [36:37<3:36:42,  1.36step/s]INFO 2026-04-07 20:12:49 ot_train.py:439 step:12K smpl:99K ep:119 epch:29.70 loss:0.239 grdn:4.851 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:  12%|█▏        | 2400/20000 [36:56<3:41:08,  1.33step/s]INFO 2026-04-07 20:13:08 ot_train.py:439 step:12K smpl:99K ep:119 epch:29.75 loss:0.232 grdn:5.121 lr:1.0e-05 updt_s:0.125 data_s:0.834
Training:  12%|█▏        | 2420/20000 [37:15<3:44:44,  1.30step/s]INFO 2026-04-07 20:13:27 ot_train.py:439 step:12K smpl:99K ep:119 epch:29.79 loss:0.225 grdn:5.274 lr:1.0e-05 updt_s:0.124 data_s:0.827
Training:  12%|█▏        | 2440/20000 [37:33<3:34:42,  1.36step/s]INFO 2026-04-07 20:13:46 ot_train.py:439 step:12K smpl:100K ep:119 epch:29.84 loss:0.229 grdn:5.973 lr:1.0e-05 updt_s:0.124 data_s:0.797
Training:  12%|█▏        | 2460/20000 [37:52<3:39:41,  1.33step/s]INFO 2026-04-07 20:14:04 ot_train.py:439 step:12K smpl:100K ep:120 epch:29.89 loss:0.238 grdn:5.451 lr:1.0e-05 updt_s:0.125 data_s:0.793
Training:  12%|█▏        | 2480/20000 [38:10<3:42:02,  1.32step/s]INFO 2026-04-07 20:14:23 ot_train.py:439 step:12K smpl:100K ep:120 epch:29.94 loss:0.230 grdn:5.066 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  12%|█▎        | 2500/20000 [38:29<3:24:38,  1.43step/s]INFO 2026-04-07 20:14:41 ot_train.py:439 step:12K smpl:100K ep:120 epch:29.99 loss:0.229 grdn:5.399 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  13%|█▎        | 2520/20000 [38:49<3:47:23,  1.28step/s]INFO 2026-04-07 20:15:02 ot_train.py:439 step:13K smpl:100K ep:120 epch:30.03 loss:0.232 grdn:6.279 lr:1.0e-05 updt_s:0.124 data_s:0.885
Training:  13%|█▎        | 2540/20000 [39:07<3:38:02,  1.33step/s]INFO 2026-04-07 20:15:20 ot_train.py:439 step:13K smpl:100K ep:120 epch:30.08 loss:0.223 grdn:5.382 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  13%|█▎        | 2560/20000 [39:26<3:56:02,  1.23step/s]INFO 2026-04-07 20:15:39 ot_train.py:439 step:13K smpl:100K ep:121 epch:30.13 loss:0.238 grdn:6.026 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  13%|█▎        | 2580/20000 [39:45<3:29:53,  1.38step/s]INFO 2026-04-07 20:15:57 ot_train.py:439 step:13K smpl:101K ep:121 epch:30.18 loss:0.240 grdn:5.560 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  13%|█▎        | 2600/20000 [40:04<3:39:38,  1.32step/s]INFO 2026-04-07 20:16:16 ot_train.py:439 step:13K smpl:101K ep:121 epch:30.22 loss:0.238 grdn:4.661 lr:1.0e-05 updt_s:0.125 data_s:0.828
Training:  13%|█▎        | 2620/20000 [40:23<3:40:34,  1.31step/s]INFO 2026-04-07 20:16:35 ot_train.py:439 step:13K smpl:101K ep:121 epch:30.27 loss:0.238 grdn:5.114 lr:1.0e-05 updt_s:0.125 data_s:0.818
Training:  13%|█▎        | 2640/20000 [40:42<3:46:29,  1.28step/s]INFO 2026-04-07 20:16:54 ot_train.py:439 step:13K smpl:101K ep:121 epch:30.32 loss:0.232 grdn:5.420 lr:1.0e-05 updt_s:0.125 data_s:0.822
Training:  13%|█▎        | 2660/20000 [41:00<3:40:17,  1.31step/s]INFO 2026-04-07 20:17:13 ot_train.py:439 step:13K smpl:101K ep:121 epch:30.37 loss:0.223 grdn:5.312 lr:1.0e-05 updt_s:0.125 data_s:0.820
Training:  13%|█▎        | 2680/20000 [41:19<3:40:53,  1.31step/s]INFO 2026-04-07 20:17:32 ot_train.py:439 step:13K smpl:101K ep:122 epch:30.42 loss:0.217 grdn:4.724 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  14%|█▎        | 2700/20000 [41:38<3:44:45,  1.28step/s]INFO 2026-04-07 20:17:51 ot_train.py:439 step:13K smpl:102K ep:122 epch:30.46 loss:0.227 grdn:5.751 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  14%|█▎        | 2720/20000 [41:57<3:38:57,  1.32step/s]INFO 2026-04-07 20:18:10 ot_train.py:439 step:13K smpl:102K ep:122 epch:30.51 loss:0.242 grdn:5.028 lr:1.0e-05 updt_s:0.125 data_s:0.834
Training:  14%|█▎        | 2740/20000 [42:16<3:35:42,  1.33step/s]INFO 2026-04-07 20:18:29 ot_train.py:439 step:13K smpl:102K ep:122 epch:30.56 loss:0.231 grdn:6.006 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  14%|█▍        | 2760/20000 [42:35<3:36:03,  1.33step/s]INFO 2026-04-07 20:18:48 ot_train.py:439 step:13K smpl:102K ep:122 epch:30.61 loss:0.226 grdn:4.968 lr:1.0e-05 updt_s:0.124 data_s:0.847
Training:  14%|█▍        | 2780/20000 [42:54<3:36:06,  1.33step/s]INFO 2026-04-07 20:19:07 ot_train.py:439 step:13K smpl:102K ep:123 epch:30.66 loss:0.248 grdn:6.658 lr:1.0e-05 updt_s:0.125 data_s:0.821
Training:  14%|█▍        | 2800/20000 [43:13<3:30:27,  1.36step/s]INFO 2026-04-07 20:19:25 ot_train.py:439 step:13K smpl:102K ep:123 epch:30.70 loss:0.242 grdn:5.591 lr:1.0e-05 updt_s:0.126 data_s:0.795
Training:  14%|█▍        | 2820/20000 [43:31<3:33:47,  1.34step/s]INFO 2026-04-07 20:19:44 ot_train.py:439 step:13K smpl:103K ep:123 epch:30.75 loss:0.228 grdn:6.029 lr:1.0e-05 updt_s:0.125 data_s:0.796
Training:  14%|█▍        | 2840/20000 [43:50<3:30:24,  1.36step/s]INFO 2026-04-07 20:20:02 ot_train.py:439 step:13K smpl:103K ep:123 epch:30.80 loss:0.228 grdn:4.971 lr:1.0e-05 updt_s:0.125 data_s:0.800
Training:  14%|█▍        | 2860/20000 [44:08<3:30:56,  1.35step/s]INFO 2026-04-07 20:20:21 ot_train.py:439 step:13K smpl:103K ep:123 epch:30.85 loss:0.228 grdn:4.611 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  14%|█▍        | 2880/20000 [44:27<3:37:41,  1.31step/s]INFO 2026-04-07 20:20:40 ot_train.py:439 step:13K smpl:103K ep:124 epch:30.90 loss:0.237 grdn:5.389 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  14%|█▍        | 2900/20000 [44:45<3:27:16,  1.38step/s]INFO 2026-04-07 20:20:58 ot_train.py:439 step:13K smpl:103K ep:124 epch:30.94 loss:0.235 grdn:5.404 lr:1.0e-05 updt_s:0.127 data_s:0.801
Training:  15%|█▍        | 2920/20000 [45:07<9:06:54,  1.92s/step]INFO 2026-04-07 20:21:19 ot_train.py:439 step:13K smpl:103K ep:124 epch:30.99 loss:0.236 grdn:4.765 lr:1.0e-05 updt_s:0.132 data_s:0.930
Training:  15%|█▍        | 2940/20000 [45:24<4:01:46,  1.18step/s]INFO 2026-04-07 20:21:37 ot_train.py:439 step:13K smpl:104K ep:124 epch:31.04 loss:0.226 grdn:5.832 lr:1.0e-05 updt_s:0.125 data_s:0.753
Training:  15%|█▍        | 2960/20000 [45:42<3:06:34,  1.52step/s]INFO 2026-04-07 20:21:54 ot_train.py:439 step:13K smpl:104K ep:124 epch:31.09 loss:0.221 grdn:4.722 lr:1.0e-05 updt_s:0.124 data_s:0.747
Training:  15%|█▍        | 2980/20000 [46:00<2:35:02,  1.83step/s]INFO 2026-04-07 20:22:12 ot_train.py:439 step:13K smpl:104K ep:125 epch:31.14 loss:0.240 grdn:5.398 lr:1.0e-05 updt_s:0.124 data_s:0.766
Training:  15%|█▌        | 3000/20000 [46:19<2:43:36,  1.73step/s]INFO 2026-04-07 20:22:31 ot_train.py:439 step:13K smpl:104K ep:125 epch:31.18 loss:0.231 grdn:5.388 lr:1.0e-05 updt_s:0.125 data_s:0.824
Training:  15%|█▌        | 3020/20000 [46:37<2:37:01,  1.80step/s]INFO 2026-04-07 20:22:50 ot_train.py:439 step:13K smpl:104K ep:125 epch:31.23 loss:0.234 grdn:5.474 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  15%|█▌        | 3040/20000 [46:56<2:34:46,  1.83step/s]INFO 2026-04-07 20:23:08 ot_train.py:439 step:13K smpl:104K ep:125 epch:31.28 loss:0.239 grdn:5.501 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  15%|█▌        | 3060/20000 [47:14<2:36:10,  1.81step/s]INFO 2026-04-07 20:23:27 ot_train.py:439 step:13K smpl:104K ep:125 epch:31.33 loss:0.237 grdn:5.175 lr:1.0e-05 updt_s:0.125 data_s:0.795
Training:  15%|█▌        | 3080/20000 [47:32<2:38:03,  1.78step/s]INFO 2026-04-07 20:23:45 ot_train.py:439 step:13K smpl:105K ep:126 epch:31.38 loss:0.231 grdn:4.818 lr:1.0e-05 updt_s:0.124 data_s:0.788
Training:  16%|█▌        | 3100/20000 [47:51<2:40:03,  1.76step/s]INFO 2026-04-07 20:24:04 ot_train.py:439 step:13K smpl:105K ep:126 epch:31.42 loss:0.223 grdn:4.866 lr:1.0e-05 updt_s:0.125 data_s:0.816
Training:  16%|█▌        | 3120/20000 [48:10<2:42:29,  1.73step/s]INFO 2026-04-07 20:24:23 ot_train.py:439 step:13K smpl:105K ep:126 epch:31.47 loss:0.235 grdn:4.953 lr:1.0e-05 updt_s:0.124 data_s:0.830
Training:  16%|█▌        | 3140/20000 [48:29<2:39:01,  1.77step/s]INFO 2026-04-07 20:24:41 ot_train.py:439 step:13K smpl:105K ep:126 epch:31.52 loss:0.225 grdn:5.494 lr:1.0e-05 updt_s:0.124 data_s:0.794
Training:  16%|█▌        | 3160/20000 [48:47<2:32:06,  1.85step/s]INFO 2026-04-07 20:25:00 ot_train.py:439 step:13K smpl:105K ep:126 epch:31.57 loss:0.225 grdn:5.144 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  16%|█▌        | 3180/20000 [49:05<2:34:47,  1.81step/s]INFO 2026-04-07 20:25:18 ot_train.py:439 step:13K smpl:105K ep:126 epch:31.62 loss:0.233 grdn:5.151 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  16%|█▌        | 3200/20000 [49:24<2:38:14,  1.77step/s]INFO 2026-04-07 20:25:36 ot_train.py:439 step:13K smpl:106K ep:127 epch:31.66 loss:0.231 grdn:5.592 lr:1.0e-05 updt_s:0.125 data_s:0.794
Training:  16%|█▌        | 3220/20000 [49:43<2:35:24,  1.80step/s]INFO 2026-04-07 20:25:55 ot_train.py:439 step:13K smpl:106K ep:127 epch:31.71 loss:0.229 grdn:5.317 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  16%|█▌        | 3240/20000 [50:01<2:33:28,  1.82step/s]INFO 2026-04-07 20:26:13 ot_train.py:439 step:13K smpl:106K ep:127 epch:31.76 loss:0.221 grdn:5.675 lr:1.0e-05 updt_s:0.125 data_s:0.784
Training:  16%|█▋        | 3260/20000 [50:19<2:34:48,  1.80step/s]INFO 2026-04-07 20:26:32 ot_train.py:439 step:13K smpl:106K ep:127 epch:31.81 loss:0.234 grdn:5.508 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:  16%|█▋        | 3280/20000 [50:38<2:36:13,  1.78step/s]INFO 2026-04-07 20:26:50 ot_train.py:439 step:13K smpl:106K ep:127 epch:31.86 loss:0.225 grdn:4.804 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  16%|█▋        | 3300/20000 [50:56<2:34:59,  1.80step/s]INFO 2026-04-07 20:27:09 ot_train.py:439 step:13K smpl:106K ep:128 epch:31.90 loss:0.236 grdn:4.972 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  17%|█▋        | 3320/20000 [51:14<2:28:45,  1.87step/s]INFO 2026-04-07 20:27:27 ot_train.py:439 step:13K smpl:107K ep:128 epch:31.95 loss:0.232 grdn:5.282 lr:1.0e-05 updt_s:0.125 data_s:0.771
Training:  17%|█▋        | 3340/20000 [51:36<7:16:56,  1.57s/step]INFO 2026-04-07 20:27:48 ot_train.py:439 step:13K smpl:107K ep:128 epch:32.00 loss:0.227 grdn:4.953 lr:1.0e-05 updt_s:0.125 data_s:0.956
Training:  17%|█▋        | 3360/20000 [51:53<5:56:54,  1.29s/step]INFO 2026-04-07 20:28:06 ot_train.py:439 step:13K smpl:107K ep:128 epch:32.05 loss:0.226 grdn:4.795 lr:1.0e-05 updt_s:0.125 data_s:0.750
Training:  17%|█▋        | 3380/20000 [52:11<5:22:40,  1.16s/step]INFO 2026-04-07 20:28:23 ot_train.py:439 step:13K smpl:107K ep:128 epch:32.10 loss:0.218 grdn:4.955 lr:1.0e-05 updt_s:0.124 data_s:0.735
Training:  17%|█▋        | 3400/20000 [52:28<4:56:32,  1.07s/step]INFO 2026-04-07 20:28:40 ot_train.py:439 step:13K smpl:107K ep:129 epch:32.14 loss:0.223 grdn:5.217 lr:1.0e-05 updt_s:0.124 data_s:0.736
Training:  17%|█▋        | 3420/20000 [52:44<4:32:39,  1.01step/s]INFO 2026-04-07 20:28:57 ot_train.py:439 step:13K smpl:107K ep:129 epch:32.19 loss:0.234 grdn:4.985 lr:1.0e-05 updt_s:0.124 data_s:0.710
Training:  17%|█▋        | 3440/20000 [53:02<4:24:53,  1.04step/s]INFO 2026-04-07 20:29:14 ot_train.py:439 step:13K smpl:108K ep:129 epch:32.24 loss:0.231 grdn:5.254 lr:1.0e-05 updt_s:0.124 data_s:0.731
Training:  17%|█▋        | 3460/20000 [53:18<3:58:50,  1.15step/s]INFO 2026-04-07 20:29:31 ot_train.py:439 step:13K smpl:108K ep:129 epch:32.29 loss:0.235 grdn:5.290 lr:1.0e-05 updt_s:0.123 data_s:0.717
Training:  17%|█▋        | 3480/20000 [53:35<2:58:53,  1.54step/s]INFO 2026-04-07 20:29:48 ot_train.py:439 step:13K smpl:108K ep:129 epch:32.34 loss:0.233 grdn:5.803 lr:1.0e-05 updt_s:0.124 data_s:0.714
Training:  18%|█▊        | 3500/20000 [53:52<2:25:39,  1.89step/s]INFO 2026-04-07 20:30:05 ot_train.py:439 step:14K smpl:108K ep:130 epch:32.38 loss:0.221 grdn:5.111 lr:1.0e-05 updt_s:0.124 data_s:0.722
Training:  18%|█▊        | 3520/20000 [54:09<2:21:45,  1.94step/s]INFO 2026-04-07 20:30:22 ot_train.py:439 step:14K smpl:108K ep:130 epch:32.43 loss:0.241 grdn:5.931 lr:1.0e-05 updt_s:0.124 data_s:0.735
Training:  18%|█▊        | 3540/20000 [54:27<2:28:20,  1.85step/s]INFO 2026-04-07 20:30:39 ot_train.py:439 step:14K smpl:108K ep:130 epch:32.48 loss:0.233 grdn:5.727 lr:1.0e-05 updt_s:0.125 data_s:0.746
Training:  18%|█▊        | 3560/20000 [54:44<2:29:57,  1.83step/s]INFO 2026-04-07 20:30:57 ot_train.py:439 step:14K smpl:108K ep:130 epch:32.53 loss:0.232 grdn:6.074 lr:1.0e-05 updt_s:0.125 data_s:0.752
Training:  18%|█▊        | 3580/20000 [55:01<2:20:05,  1.95step/s]INFO 2026-04-07 20:31:14 ot_train.py:439 step:14K smpl:109K ep:130 epch:32.58 loss:0.237 grdn:6.549 lr:1.0e-05 updt_s:0.124 data_s:0.718
Training:  18%|█▊        | 3600/20000 [55:18<2:33:28,  1.78step/s]INFO 2026-04-07 20:31:31 ot_train.py:439 step:14K smpl:109K ep:130 epch:32.62 loss:0.227 grdn:4.951 lr:1.0e-05 updt_s:0.124 data_s:0.739
Training:  18%|█▊        | 3620/20000 [55:36<2:40:00,  1.71step/s]INFO 2026-04-07 20:31:49 ot_train.py:439 step:14K smpl:109K ep:131 epch:32.67 loss:0.242 grdn:5.353 lr:1.0e-05 updt_s:0.124 data_s:0.766
Training:  18%|█▊        | 3640/20000 [55:53<2:30:05,  1.82step/s]INFO 2026-04-07 20:32:06 ot_train.py:439 step:14K smpl:109K ep:131 epch:32.72 loss:0.221 grdn:4.554 lr:1.0e-05 updt_s:0.125 data_s:0.734
Training:  18%|█▊        | 3660/20000 [56:11<2:23:41,  1.90step/s]INFO 2026-04-07 20:32:23 ot_train.py:439 step:14K smpl:109K ep:131 epch:32.77 loss:0.220 grdn:4.956 lr:1.0e-05 updt_s:0.125 data_s:0.728
Training:  18%|█▊        | 3680/20000 [56:28<2:23:10,  1.90step/s]INFO 2026-04-07 20:32:41 ot_train.py:439 step:14K smpl:109K ep:131 epch:32.82 loss:0.220 grdn:4.505 lr:1.0e-05 updt_s:0.124 data_s:0.750
Training:  18%|█▊        | 3700/20000 [56:46<2:25:12,  1.87step/s]INFO 2026-04-07 20:32:58 ot_train.py:439 step:14K smpl:110K ep:131 epch:32.86 loss:0.225 grdn:4.940 lr:1.0e-05 updt_s:0.124 data_s:0.758
Training:  19%|█▊        | 3720/20000 [57:03<2:26:16,  1.85step/s]INFO 2026-04-07 20:33:16 ot_train.py:439 step:14K smpl:110K ep:132 epch:32.91 loss:0.232 grdn:4.938 lr:1.0e-05 updt_s:0.124 data_s:0.757
Training:  19%|█▊        | 3740/20000 [57:21<2:28:15,  1.83step/s]INFO 2026-04-07 20:33:33 ot_train.py:439 step:14K smpl:110K ep:132 epch:32.96 loss:0.215 grdn:4.964 lr:1.0e-05 updt_s:0.124 data_s:0.752
Training:  19%|█▉        | 3760/20000 [57:39<2:52:24,  1.57step/s]INFO 2026-04-07 20:33:52 ot_train.py:439 step:14K smpl:110K ep:132 epch:33.01 loss:0.232 grdn:4.832 lr:1.0e-05 updt_s:0.123 data_s:0.792
Training:  19%|█▉        | 3780/20000 [57:58<2:34:33,  1.75step/s]INFO 2026-04-07 20:34:11 ot_train.py:439 step:14K smpl:110K ep:132 epch:33.06 loss:0.223 grdn:5.234 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  19%|█▉        | 3800/20000 [58:17<2:32:54,  1.77step/s]INFO 2026-04-07 20:34:29 ot_train.py:439 step:14K smpl:110K ep:132 epch:33.10 loss:0.228 grdn:5.313 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  19%|█▉        | 3820/20000 [58:36<2:34:04,  1.75step/s]INFO 2026-04-07 20:34:48 ot_train.py:439 step:14K smpl:111K ep:133 epch:33.15 loss:0.231 grdn:5.158 lr:1.0e-05 updt_s:0.124 data_s:0.815
Training:  19%|█▉        | 3840/20000 [58:55<2:29:05,  1.81step/s]INFO 2026-04-07 20:35:08 ot_train.py:439 step:14K smpl:111K ep:133 epch:33.20 loss:0.222 grdn:5.617 lr:1.0e-05 updt_s:0.124 data_s:0.842
Training:  19%|█▉        | 3860/20000 [59:14<2:40:38,  1.67step/s]INFO 2026-04-07 20:35:27 ot_train.py:439 step:14K smpl:111K ep:133 epch:33.25 loss:0.228 grdn:5.002 lr:1.0e-05 updt_s:0.124 data_s:0.847
Training:  19%|█▉        | 3880/20000 [59:33<2:30:14,  1.79step/s]INFO 2026-04-07 20:35:46 ot_train.py:439 step:14K smpl:111K ep:133 epch:33.30 loss:0.225 grdn:4.625 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  20%|█▉        | 3900/20000 [59:52<2:30:47,  1.78step/s]INFO 2026-04-07 20:36:05 ot_train.py:439 step:14K smpl:111K ep:133 epch:33.34 loss:0.224 grdn:5.002 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  20%|█▉        | 3920/20000 [1:00:11<2:30:47,  1.78step/s]INFO 2026-04-07 20:36:24 ot_train.py:439 step:14K smpl:111K ep:134 epch:33.39 loss:0.228 grdn:4.524 lr:1.0e-05 updt_s:0.125 data_s:0.822
Training:  20%|█▉        | 3940/20000 [1:00:30<2:29:03,  1.80step/s]INFO 2026-04-07 20:36:43 ot_train.py:439 step:14K smpl:112K ep:134 epch:33.44 loss:0.231 grdn:4.831 lr:1.0e-05 updt_s:0.125 data_s:0.805
Training:  20%|█▉        | 3960/20000 [1:00:49<2:35:47,  1.72step/s]INFO 2026-04-07 20:37:02 ot_train.py:439 step:14K smpl:112K ep:134 epch:33.49 loss:0.223 grdn:5.063 lr:1.0e-05 updt_s:0.125 data_s:0.826
Training:  20%|█▉        | 3980/20000 [1:01:08<2:33:21,  1.74step/s]INFO 2026-04-07 20:37:20 ot_train.py:439 step:14K smpl:112K ep:134 epch:33.54 loss:0.220 grdn:5.397 lr:1.0e-05 updt_s:0.127 data_s:0.810
Training:  20%|██        | 4000/20000 [1:01:27<2:32:50,  1.74step/s]INFO 2026-04-07 20:37:39 ot_train.py:439 step:14K smpl:112K ep:134 epch:33.58 loss:0.224 grdn:5.981 lr:1.0e-05 updt_s:0.127 data_s:0.823
Training:  20%|██        | 4020/20000 [1:01:46<2:36:51,  1.70step/s]INFO 2026-04-07 20:37:59 ot_train.py:439 step:14K smpl:112K ep:135 epch:33.63 loss:0.235 grdn:5.857 lr:1.0e-05 updt_s:0.125 data_s:0.845
Training:  20%|██        | 4040/20000 [1:02:05<2:25:52,  1.82step/s]INFO 2026-04-07 20:38:17 ot_train.py:439 step:14K smpl:112K ep:135 epch:33.68 loss:0.227 grdn:5.230 lr:1.0e-05 updt_s:0.125 data_s:0.801
Training:  20%|██        | 4060/20000 [1:02:23<2:34:48,  1.72step/s]INFO 2026-04-07 20:38:35 ot_train.py:439 step:14K smpl:112K ep:135 epch:33.73 loss:0.229 grdn:4.766 lr:1.0e-05 updt_s:0.125 data_s:0.777
Training:  20%|██        | 4080/20000 [1:02:42<2:23:54,  1.84step/s]INFO 2026-04-07 20:38:54 ot_train.py:439 step:14K smpl:113K ep:135 epch:33.78 loss:0.220 grdn:5.156 lr:1.0e-05 updt_s:0.135 data_s:0.808
Training:  20%|██        | 4100/20000 [1:03:01<2:32:33,  1.74step/s]INFO 2026-04-07 20:39:13 ot_train.py:439 step:14K smpl:113K ep:135 epch:33.82 loss:0.230 grdn:5.937 lr:1.0e-05 updt_s:0.126 data_s:0.821
Training:  21%|██        | 4120/20000 [1:03:18<2:20:39,  1.88step/s]INFO 2026-04-07 20:39:31 ot_train.py:439 step:14K smpl:113K ep:135 epch:33.87 loss:0.227 grdn:5.286 lr:1.0e-05 updt_s:0.125 data_s:0.761
Training:  21%|██        | 4140/20000 [1:03:37<2:27:37,  1.79step/s]INFO 2026-04-07 20:39:49 ot_train.py:439 step:14K smpl:113K ep:136 epch:33.92 loss:0.225 grdn:4.949 lr:1.0e-05 updt_s:0.125 data_s:0.787
Training:  21%|██        | 4160/20000 [1:03:54<2:26:23,  1.80step/s]INFO 2026-04-07 20:40:07 ot_train.py:439 step:14K smpl:113K ep:136 epch:33.97 loss:0.229 grdn:6.164 lr:1.0e-05 updt_s:0.125 data_s:0.764
Training:  21%|██        | 4180/20000 [1:04:16<3:36:16,  1.22step/s]INFO 2026-04-07 20:40:29 ot_train.py:439 step:14K smpl:113K ep:136 epch:34.01 loss:0.219 grdn:6.412 lr:1.0e-05 updt_s:0.123 data_s:0.959
Training:  21%|██        | 4200/20000 [1:04:35<4:00:28,  1.10step/s]INFO 2026-04-07 20:40:47 ot_train.py:439 step:14K smpl:114K ep:136 epch:34.06 loss:0.222 grdn:4.940 lr:1.0e-05 updt_s:0.124 data_s:0.815
Training:  21%|██        | 4220/20000 [1:04:53<4:08:24,  1.06step/s]INFO 2026-04-07 20:41:06 ot_train.py:439 step:14K smpl:114K ep:136 epch:34.11 loss:0.228 grdn:5.072 lr:1.0e-05 updt_s:0.124 data_s:0.786
Training:  21%|██        | 4240/20000 [1:05:12<4:48:05,  1.10s/step]INFO 2026-04-07 20:41:25 ot_train.py:439 step:14K smpl:114K ep:137 epch:34.16 loss:0.214 grdn:4.789 lr:1.0e-05 updt_s:0.124 data_s:0.842
Training:  21%|██▏       | 4260/20000 [1:05:31<4:35:14,  1.05s/step]INFO 2026-04-07 20:41:44 ot_train.py:439 step:14K smpl:114K ep:137 epch:34.21 loss:0.220 grdn:5.033 lr:1.0e-05 updt_s:0.123 data_s:0.815
Training:  21%|██▏       | 4280/20000 [1:05:50<4:53:35,  1.12s/step]INFO 2026-04-07 20:42:03 ot_train.py:439 step:14K smpl:114K ep:137 epch:34.25 loss:0.224 grdn:4.678 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  22%|██▏       | 4300/20000 [1:06:09<4:44:06,  1.09s/step]INFO 2026-04-07 20:42:21 ot_train.py:439 step:14K smpl:114K ep:137 epch:34.30 loss:0.227 grdn:5.422 lr:1.0e-05 updt_s:0.124 data_s:0.817
Training:  22%|██▏       | 4320/20000 [1:06:27<4:44:11,  1.09s/step]INFO 2026-04-07 20:42:40 ot_train.py:439 step:14K smpl:115K ep:137 epch:34.35 loss:0.222 grdn:4.982 lr:1.0e-05 updt_s:0.125 data_s:0.783
Training:  22%|██▏       | 4340/20000 [1:06:45<4:27:35,  1.03s/step]INFO 2026-04-07 20:42:58 ot_train.py:439 step:14K smpl:115K ep:138 epch:34.40 loss:0.225 grdn:4.904 lr:1.0e-05 updt_s:0.125 data_s:0.787
Training:  22%|██▏       | 4360/20000 [1:07:04<4:36:07,  1.06s/step]INFO 2026-04-07 20:43:17 ot_train.py:439 step:14K smpl:115K ep:138 epch:34.45 loss:0.231 grdn:5.376 lr:1.0e-05 updt_s:0.124 data_s:0.825
Training:  22%|██▏       | 4380/20000 [1:07:23<4:28:32,  1.03s/step]INFO 2026-04-07 20:43:36 ot_train.py:439 step:14K smpl:115K ep:138 epch:34.49 loss:0.230 grdn:5.806 lr:1.0e-05 updt_s:0.126 data_s:0.820
Training:  22%|██▏       | 4400/20000 [1:07:42<4:28:43,  1.03s/step]INFO 2026-04-07 20:43:55 ot_train.py:439 step:14K smpl:115K ep:138 epch:34.54 loss:0.225 grdn:5.617 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:  22%|██▏       | 4420/20000 [1:08:01<4:22:45,  1.01s/step]INFO 2026-04-07 20:44:14 ot_train.py:439 step:14K smpl:115K ep:138 epch:34.59 loss:0.225 grdn:5.735 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  22%|██▏       | 4440/20000 [1:08:20<4:34:00,  1.06s/step]INFO 2026-04-07 20:44:33 ot_train.py:439 step:14K smpl:116K ep:139 epch:34.64 loss:0.227 grdn:5.551 lr:1.0e-05 updt_s:0.124 data_s:0.824
Training:  22%|██▏       | 4460/20000 [1:08:39<4:19:43,  1.00s/step]INFO 2026-04-07 20:44:51 ot_train.py:439 step:14K smpl:116K ep:139 epch:34.69 loss:0.222 grdn:4.358 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  22%|██▏       | 4480/20000 [1:08:57<4:09:37,  1.04step/s]INFO 2026-04-07 20:45:09 ot_train.py:439 step:14K smpl:116K ep:139 epch:34.73 loss:0.219 grdn:4.674 lr:1.0e-05 updt_s:0.125 data_s:0.789
Training:  22%|██▎       | 4500/20000 [1:09:16<4:21:51,  1.01s/step]INFO 2026-04-07 20:45:28 ot_train.py:439 step:14K smpl:116K ep:139 epch:34.78 loss:0.213 grdn:4.733 lr:1.0e-05 updt_s:0.126 data_s:0.808
Training:  23%|██▎       | 4520/20000 [1:09:34<4:12:35,  1.02step/s]INFO 2026-04-07 20:45:46 ot_train.py:439 step:15K smpl:116K ep:139 epch:34.83 loss:0.228 grdn:4.971 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:  23%|██▎       | 4540/20000 [1:09:53<4:11:11,  1.03step/s]INFO 2026-04-07 20:46:05 ot_train.py:439 step:15K smpl:116K ep:140 epch:34.88 loss:0.221 grdn:5.075 lr:1.0e-05 updt_s:0.127 data_s:0.808
Training:  23%|██▎       | 4560/20000 [1:10:11<4:21:28,  1.02s/step]INFO 2026-04-07 20:46:24 ot_train.py:439 step:15K smpl:116K ep:140 epch:34.93 loss:0.229 grdn:4.681 lr:1.0e-05 updt_s:0.125 data_s:0.812
Training:  23%|██▎       | 4580/20000 [1:10:30<4:23:07,  1.02s/step]INFO 2026-04-07 20:46:43 ot_train.py:439 step:15K smpl:117K ep:140 epch:34.97 loss:0.225 grdn:5.264 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  23%|██▎       | 4600/20000 [1:10:49<4:15:10,  1.01step/s]INFO 2026-04-07 20:47:01 ot_train.py:439 step:15K smpl:117K ep:140 epch:35.02 loss:0.222 grdn:4.998 lr:1.0e-05 updt_s:0.123 data_s:0.815
Training:  23%|██▎       | 4620/20000 [1:11:07<4:04:49,  1.05step/s]INFO 2026-04-07 20:47:19 ot_train.py:439 step:15K smpl:117K ep:140 epch:35.07 loss:0.227 grdn:5.092 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:  23%|██▎       | 4640/20000 [1:11:25<3:59:34,  1.07step/s]INFO 2026-04-07 20:47:38 ot_train.py:439 step:15K smpl:117K ep:140 epch:35.12 loss:0.221 grdn:5.753 lr:1.0e-05 updt_s:0.124 data_s:0.792
Training:  23%|██▎       | 4660/20000 [1:11:44<3:47:17,  1.12step/s]INFO 2026-04-07 20:47:57 ot_train.py:439 step:15K smpl:117K ep:141 epch:35.17 loss:0.224 grdn:4.702 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  23%|██▎       | 4680/20000 [1:12:02<3:17:01,  1.30step/s]INFO 2026-04-07 20:48:15 ot_train.py:439 step:15K smpl:117K ep:141 epch:35.21 loss:0.218 grdn:5.425 lr:1.0e-05 updt_s:0.123 data_s:0.780
Training:  24%|██▎       | 4700/20000 [1:12:20<3:04:17,  1.38step/s]INFO 2026-04-07 20:48:33 ot_train.py:439 step:15K smpl:118K ep:141 epch:35.26 loss:0.222 grdn:4.955 lr:1.0e-05 updt_s:0.123 data_s:0.801
Training:  24%|██▎       | 4720/20000 [1:12:39<3:09:56,  1.34step/s]INFO 2026-04-07 20:48:52 ot_train.py:439 step:15K smpl:118K ep:141 epch:35.31 loss:0.231 grdn:5.585 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:  24%|██▎       | 4740/20000 [1:12:57<2:50:04,  1.50step/s]INFO 2026-04-07 20:49:10 ot_train.py:439 step:15K smpl:118K ep:141 epch:35.36 loss:0.224 grdn:4.556 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  24%|██▍       | 4760/20000 [1:13:15<2:26:16,  1.74step/s]INFO 2026-04-07 20:49:28 ot_train.py:439 step:15K smpl:118K ep:142 epch:35.41 loss:0.226 grdn:4.984 lr:1.0e-05 updt_s:0.124 data_s:0.780
Training:  24%|██▍       | 4780/20000 [1:13:35<2:30:52,  1.68step/s]INFO 2026-04-07 20:49:47 ot_train.py:439 step:15K smpl:118K ep:142 epch:35.45 loss:0.224 grdn:5.574 lr:1.0e-05 updt_s:0.125 data_s:0.828
Training:  24%|██▍       | 4800/20000 [1:13:53<2:17:37,  1.84step/s]INFO 2026-04-07 20:50:05 ot_train.py:439 step:15K smpl:118K ep:142 epch:35.50 loss:0.219 grdn:4.738 lr:1.0e-05 updt_s:0.124 data_s:0.792
Training:  24%|██▍       | 4820/20000 [1:14:12<2:25:48,  1.74step/s]INFO 2026-04-07 20:50:24 ot_train.py:439 step:15K smpl:119K ep:142 epch:35.55 loss:0.218 grdn:4.752 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  24%|██▍       | 4840/20000 [1:14:31<2:29:07,  1.69step/s]INFO 2026-04-07 20:50:44 ot_train.py:439 step:15K smpl:119K ep:142 epch:35.60 loss:0.231 grdn:4.965 lr:1.0e-05 updt_s:0.124 data_s:0.842
Training:  24%|██▍       | 4860/20000 [1:14:49<2:19:00,  1.82step/s]INFO 2026-04-07 20:51:02 ot_train.py:439 step:15K smpl:119K ep:143 epch:35.65 loss:0.208 grdn:4.799 lr:1.0e-05 updt_s:0.125 data_s:0.777
Training:  24%|██▍       | 4880/20000 [1:15:08<2:17:26,  1.83step/s]INFO 2026-04-07 20:51:20 ot_train.py:439 step:15K smpl:119K ep:143 epch:35.69 loss:0.215 grdn:5.477 lr:1.0e-05 updt_s:0.127 data_s:0.791
Training:  24%|██▍       | 4900/20000 [1:15:26<2:19:28,  1.80step/s]INFO 2026-04-07 20:51:39 ot_train.py:439 step:15K smpl:119K ep:143 epch:35.74 loss:0.226 grdn:5.373 lr:1.0e-05 updt_s:0.125 data_s:0.794
Training:  25%|██▍       | 4920/20000 [1:15:44<2:13:12,  1.89step/s]INFO 2026-04-07 20:51:56 ot_train.py:439 step:15K smpl:119K ep:143 epch:35.79 loss:0.229 grdn:5.187 lr:1.0e-05 updt_s:0.124 data_s:0.760
Training:  25%|██▍       | 4940/20000 [1:16:02<2:19:18,  1.80step/s]INFO 2026-04-07 20:52:14 ot_train.py:439 step:15K smpl:120K ep:143 epch:35.84 loss:0.217 grdn:5.349 lr:1.0e-05 updt_s:0.124 data_s:0.774
Training:  25%|██▍       | 4960/20000 [1:16:21<2:19:21,  1.80step/s]INFO 2026-04-07 20:52:33 ot_train.py:439 step:15K smpl:120K ep:144 epch:35.89 loss:0.215 grdn:5.571 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  25%|██▍       | 4980/20000 [1:16:39<2:20:46,  1.78step/s]INFO 2026-04-07 20:52:52 ot_train.py:439 step:15K smpl:120K ep:144 epch:35.93 loss:0.219 grdn:5.433 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  25%|██▌       | 5000/20000 [1:16:58<2:17:55,  1.81step/s]INFO 2026-04-07 20:53:10 ot_train.py:439 step:15K smpl:120K ep:144 epch:35.98 loss:0.224 grdn:4.869 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  25%|██▌       | 5020/20000 [1:17:20<5:17:29,  1.27s/step]INFO 2026-04-07 20:53:32 ot_train.py:439 step:15K smpl:120K ep:144 epch:36.03 loss:0.219 grdn:5.384 lr:1.0e-05 updt_s:0.124 data_s:0.963
Training:  25%|██▌       | 5040/20000 [1:17:37<3:47:42,  1.09step/s]INFO 2026-04-07 20:53:50 ot_train.py:439 step:15K smpl:120K ep:144 epch:36.08 loss:0.210 grdn:5.195 lr:1.0e-05 updt_s:0.123 data_s:0.742
Training:  25%|██▌       | 5060/20000 [1:17:54<3:18:01,  1.26step/s]INFO 2026-04-07 20:54:07 ot_train.py:439 step:15K smpl:120K ep:145 epch:36.13 loss:0.218 grdn:4.619 lr:1.0e-05 updt_s:0.124 data_s:0.752
Training:  25%|██▌       | 5080/20000 [1:18:13<3:21:50,  1.23step/s]INFO 2026-04-07 20:54:25 ot_train.py:439 step:15K smpl:121K ep:145 epch:36.17 loss:0.215 grdn:4.647 lr:1.0e-05 updt_s:0.124 data_s:0.793
Training:  26%|██▌       | 5100/20000 [1:18:31<3:18:48,  1.25step/s]INFO 2026-04-07 20:54:44 ot_train.py:439 step:15K smpl:121K ep:145 epch:36.22 loss:0.230 grdn:4.981 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  26%|██▌       | 5120/20000 [1:18:50<3:11:21,  1.30step/s]INFO 2026-04-07 20:55:03 ot_train.py:439 step:15K smpl:121K ep:145 epch:36.27 loss:0.212 grdn:4.590 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  26%|██▌       | 5140/20000 [1:19:09<3:25:18,  1.21step/s]INFO 2026-04-07 20:55:21 ot_train.py:439 step:15K smpl:121K ep:145 epch:36.32 loss:0.220 grdn:5.243 lr:1.0e-05 updt_s:0.123 data_s:0.813
Training:  26%|██▌       | 5160/20000 [1:19:27<3:21:19,  1.23step/s]INFO 2026-04-07 20:55:40 ot_train.py:439 step:15K smpl:121K ep:145 epch:36.37 loss:0.217 grdn:5.281 lr:1.0e-05 updt_s:0.124 data_s:0.793
Training:  26%|██▌       | 5180/20000 [1:19:45<3:14:17,  1.27step/s]INFO 2026-04-07 20:55:58 ot_train.py:439 step:15K smpl:121K ep:146 epch:36.41 loss:0.217 grdn:5.111 lr:1.0e-05 updt_s:0.125 data_s:0.768
Training:  26%|██▌       | 5200/20000 [1:20:03<3:05:40,  1.33step/s]INFO 2026-04-07 20:56:16 ot_train.py:439 step:15K smpl:122K ep:146 epch:36.46 loss:0.222 grdn:5.521 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:  26%|██▌       | 5220/20000 [1:20:22<3:27:40,  1.19step/s]INFO 2026-04-07 20:56:35 ot_train.py:439 step:15K smpl:122K ep:146 epch:36.51 loss:0.221 grdn:4.963 lr:1.0e-05 updt_s:0.124 data_s:0.815
Training:  26%|██▌       | 5240/20000 [1:20:41<3:45:19,  1.09step/s]INFO 2026-04-07 20:56:54 ot_train.py:439 step:15K smpl:122K ep:146 epch:36.56 loss:0.223 grdn:5.038 lr:1.0e-05 updt_s:0.134 data_s:0.816
Training:  26%|██▋       | 5260/20000 [1:20:59<3:40:37,  1.11step/s]INFO 2026-04-07 20:57:12 ot_train.py:439 step:15K smpl:122K ep:146 epch:36.61 loss:0.219 grdn:4.930 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  26%|██▋       | 5280/20000 [1:21:18<3:54:30,  1.05step/s]INFO 2026-04-07 20:57:31 ot_train.py:439 step:15K smpl:122K ep:147 epch:36.65 loss:0.215 grdn:5.103 lr:1.0e-05 updt_s:0.123 data_s:0.799
Training:  26%|██▋       | 5300/20000 [1:21:36<3:41:58,  1.10step/s]INFO 2026-04-07 20:57:48 ot_train.py:439 step:15K smpl:122K ep:147 epch:36.70 loss:0.224 grdn:5.245 lr:1.0e-05 updt_s:0.125 data_s:0.765
Training:  27%|██▋       | 5320/20000 [1:21:54<3:45:02,  1.09step/s]INFO 2026-04-07 20:58:07 ot_train.py:439 step:15K smpl:123K ep:147 epch:36.75 loss:0.224 grdn:6.021 lr:1.0e-05 updt_s:0.124 data_s:0.786
Training:  27%|██▋       | 5340/20000 [1:22:12<3:27:59,  1.17step/s]INFO 2026-04-07 20:58:24 ot_train.py:439 step:15K smpl:123K ep:147 epch:36.80 loss:0.220 grdn:4.803 lr:1.0e-05 updt_s:0.125 data_s:0.767
Training:  27%|██▋       | 5360/20000 [1:22:30<3:36:23,  1.13step/s]INFO 2026-04-07 20:58:43 ot_train.py:439 step:15K smpl:123K ep:147 epch:36.85 loss:0.215 grdn:4.637 lr:1.0e-05 updt_s:0.125 data_s:0.784
Training:  27%|██▋       | 5380/20000 [1:22:48<3:38:16,  1.12step/s]INFO 2026-04-07 20:59:01 ot_train.py:439 step:15K smpl:123K ep:148 epch:36.89 loss:0.220 grdn:4.787 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  27%|██▋       | 5400/20000 [1:23:07<3:36:56,  1.12step/s]INFO 2026-04-07 20:59:19 ot_train.py:439 step:15K smpl:123K ep:148 epch:36.94 loss:0.221 grdn:5.371 lr:1.0e-05 updt_s:0.123 data_s:0.786
Training:  27%|██▋       | 5420/20000 [1:23:24<3:07:57,  1.29step/s]INFO 2026-04-07 20:59:37 ot_train.py:439 step:15K smpl:123K ep:148 epch:36.99 loss:0.225 grdn:4.720 lr:1.0e-05 updt_s:0.124 data_s:0.757
Training:  27%|██▋       | 5440/20000 [1:23:44<2:20:14,  1.73step/s]INFO 2026-04-07 20:59:57 ot_train.py:439 step:15K smpl:124K ep:148 epch:37.04 loss:0.223 grdn:4.922 lr:1.0e-05 updt_s:0.124 data_s:0.874
Training:  27%|██▋       | 5460/20000 [1:24:02<2:01:24,  2.00step/s]INFO 2026-04-07 21:00:14 ot_train.py:439 step:15K smpl:124K ep:148 epch:37.09 loss:0.209 grdn:4.326 lr:1.0e-05 updt_s:0.124 data_s:0.752
Training:  27%|██▋       | 5480/20000 [1:24:20<2:39:03,  1.52step/s]INFO 2026-04-07 21:00:32 ot_train.py:439 step:15K smpl:124K ep:149 epch:37.13 loss:0.220 grdn:4.695 lr:1.0e-05 updt_s:0.124 data_s:0.771
Training:  28%|██▊       | 5500/20000 [1:24:38<2:53:13,  1.40step/s]INFO 2026-04-07 21:00:51 ot_train.py:439 step:16K smpl:124K ep:149 epch:37.18 loss:0.220 grdn:5.837 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  28%|██▊       | 5520/20000 [1:24:57<2:52:06,  1.40step/s]INFO 2026-04-07 21:01:09 ot_train.py:439 step:16K smpl:124K ep:149 epch:37.23 loss:0.218 grdn:4.783 lr:1.0e-05 updt_s:0.123 data_s:0.802
Training:  28%|██▊       | 5540/20000 [1:25:15<2:46:06,  1.45step/s]INFO 2026-04-07 21:01:27 ot_train.py:439 step:16K smpl:124K ep:149 epch:37.28 loss:0.218 grdn:5.142 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:  28%|██▊       | 5560/20000 [1:25:33<2:42:34,  1.48step/s]INFO 2026-04-07 21:01:46 ot_train.py:439 step:16K smpl:124K ep:149 epch:37.33 loss:0.213 grdn:4.319 lr:1.0e-05 updt_s:0.124 data_s:0.794
Training:  28%|██▊       | 5580/20000 [1:25:52<2:55:35,  1.37step/s]INFO 2026-04-07 21:02:04 ot_train.py:439 step:16K smpl:125K ep:149 epch:37.37 loss:0.214 grdn:4.602 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  28%|██▊       | 5600/20000 [1:26:10<2:58:15,  1.35step/s]INFO 2026-04-07 21:02:23 ot_train.py:439 step:16K smpl:125K ep:150 epch:37.42 loss:0.210 grdn:5.372 lr:1.0e-05 updt_s:0.123 data_s:0.798
Training:  28%|██▊       | 5620/20000 [1:26:28<2:24:33,  1.66step/s]INFO 2026-04-07 21:02:41 ot_train.py:439 step:16K smpl:125K ep:150 epch:37.47 loss:0.223 grdn:4.855 lr:1.0e-05 updt_s:0.123 data_s:0.782
Training:  28%|██▊       | 5640/20000 [1:26:47<2:14:00,  1.79step/s]INFO 2026-04-07 21:02:59 ot_train.py:439 step:16K smpl:125K ep:150 epch:37.52 loss:0.222 grdn:5.093 lr:1.0e-05 updt_s:0.125 data_s:0.785
Training:  28%|██▊       | 5660/20000 [1:27:05<2:11:12,  1.82step/s]INFO 2026-04-07 21:03:18 ot_train.py:439 step:16K smpl:125K ep:150 epch:37.57 loss:0.222 grdn:5.474 lr:1.0e-05 updt_s:0.125 data_s:0.799
Training:  28%|██▊       | 5680/20000 [1:27:23<2:09:37,  1.84step/s]INFO 2026-04-07 21:03:36 ot_train.py:439 step:16K smpl:125K ep:150 epch:37.61 loss:0.213 grdn:5.507 lr:1.0e-05 updt_s:0.125 data_s:0.776
Training:  28%|██▊       | 5700/20000 [1:27:42<2:18:04,  1.73step/s]INFO 2026-04-07 21:03:54 ot_train.py:439 step:16K smpl:126K ep:151 epch:37.66 loss:0.219 grdn:5.284 lr:1.0e-05 updt_s:0.125 data_s:0.807
Training:  29%|██▊       | 5720/20000 [1:28:00<2:08:37,  1.85step/s]INFO 2026-04-07 21:04:13 ot_train.py:439 step:16K smpl:126K ep:151 epch:37.71 loss:0.223 grdn:5.678 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  29%|██▊       | 5740/20000 [1:28:19<2:17:26,  1.73step/s]INFO 2026-04-07 21:04:31 ot_train.py:439 step:16K smpl:126K ep:151 epch:37.76 loss:0.221 grdn:5.800 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:  29%|██▉       | 5760/20000 [1:28:38<2:17:21,  1.73step/s]INFO 2026-04-07 21:04:50 ot_train.py:439 step:16K smpl:126K ep:151 epch:37.81 loss:0.217 grdn:4.569 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  29%|██▉       | 5780/20000 [1:28:56<2:18:01,  1.72step/s]INFO 2026-04-07 21:05:09 ot_train.py:439 step:16K smpl:126K ep:151 epch:37.85 loss:0.209 grdn:4.674 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  29%|██▉       | 5800/20000 [1:29:14<2:07:38,  1.85step/s]INFO 2026-04-07 21:05:27 ot_train.py:439 step:16K smpl:126K ep:152 epch:37.90 loss:0.210 grdn:4.590 lr:1.0e-05 updt_s:0.125 data_s:0.768
Training:  29%|██▉       | 5820/20000 [1:29:33<2:13:08,  1.78step/s]INFO 2026-04-07 21:05:46 ot_train.py:439 step:16K smpl:127K ep:152 epch:37.95 loss:0.218 grdn:5.271 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  29%|██▉       | 5840/20000 [1:29:54<5:11:02,  1.32s/step]INFO 2026-04-07 21:06:07 ot_train.py:439 step:16K smpl:127K ep:152 epch:38.00 loss:0.217 grdn:5.253 lr:1.0e-05 updt_s:0.123 data_s:0.922
Training:  29%|██▉       | 5860/20000 [1:30:13<3:05:06,  1.27step/s]INFO 2026-04-07 21:06:25 ot_train.py:439 step:16K smpl:127K ep:152 epch:38.04 loss:0.212 grdn:5.136 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  29%|██▉       | 5880/20000 [1:30:31<2:49:17,  1.39step/s]INFO 2026-04-07 21:06:44 ot_train.py:439 step:16K smpl:127K ep:152 epch:38.09 loss:0.223 grdn:5.400 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  30%|██▉       | 5900/20000 [1:30:50<3:19:10,  1.18step/s]INFO 2026-04-07 21:07:03 ot_train.py:439 step:16K smpl:127K ep:153 epch:38.14 loss:0.210 grdn:4.177 lr:1.0e-05 updt_s:0.123 data_s:0.817
Training:  30%|██▉       | 5920/20000 [1:31:09<3:54:40,  1.00s/step]INFO 2026-04-07 21:07:22 ot_train.py:439 step:16K smpl:127K ep:153 epch:38.19 loss:0.217 grdn:4.921 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  30%|██▉       | 5940/20000 [1:31:27<3:53:27,  1.00step/s]INFO 2026-04-07 21:07:40 ot_train.py:439 step:16K smpl:128K ep:153 epch:38.24 loss:0.210 grdn:5.043 lr:1.0e-05 updt_s:0.123 data_s:0.792
Training:  30%|██▉       | 5960/20000 [1:31:46<4:00:40,  1.03s/step]INFO 2026-04-07 21:07:59 ot_train.py:439 step:16K smpl:128K ep:153 epch:38.28 loss:0.212 grdn:5.156 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  30%|██▉       | 5980/20000 [1:32:05<3:33:31,  1.09step/s]INFO 2026-04-07 21:08:17 ot_train.py:439 step:16K smpl:128K ep:153 epch:38.33 loss:0.211 grdn:5.971 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  30%|███       | 6000/20000 [1:32:23<3:56:34,  1.01s/step]INFO 2026-04-07 21:08:36 ot_train.py:439 step:16K smpl:128K ep:154 epch:38.38 loss:0.217 grdn:5.061 lr:1.0e-05 updt_s:0.123 data_s:0.812
Training:  30%|███       | 6020/20000 [1:32:42<4:19:11,  1.11s/step]INFO 2026-04-07 21:08:55 ot_train.py:439 step:16K smpl:128K ep:154 epch:38.43 loss:0.208 grdn:4.811 lr:1.0e-05 updt_s:0.123 data_s:0.816
Training:  30%|███       | 6040/20000 [1:33:01<4:37:04,  1.19s/step]INFO 2026-04-07 21:09:14 ot_train.py:439 step:16K smpl:128K ep:154 epch:38.48 loss:0.214 grdn:4.603 lr:1.0e-05 updt_s:0.124 data_s:0.831
Training:  30%|███       | 6060/20000 [1:33:19<3:54:35,  1.01s/step]INFO 2026-04-07 21:09:32 ot_train.py:439 step:16K smpl:128K ep:154 epch:38.52 loss:0.213 grdn:5.143 lr:1.0e-05 updt_s:0.123 data_s:0.785
Training:  30%|███       | 6080/20000 [1:33:38<3:53:11,  1.01s/step]INFO 2026-04-07 21:09:51 ot_train.py:439 step:16K smpl:129K ep:154 epch:38.57 loss:0.225 grdn:5.301 lr:1.0e-05 updt_s:0.123 data_s:0.817
Training:  30%|███       | 6100/20000 [1:33:57<4:00:58,  1.04s/step]INFO 2026-04-07 21:10:10 ot_train.py:439 step:16K smpl:129K ep:154 epch:38.62 loss:0.219 grdn:5.482 lr:1.0e-05 updt_s:0.124 data_s:0.832
Training:  31%|███       | 6120/20000 [1:34:16<4:10:27,  1.08s/step]INFO 2026-04-07 21:10:29 ot_train.py:439 step:16K smpl:129K ep:155 epch:38.67 loss:0.217 grdn:5.446 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  31%|███       | 6140/20000 [1:34:36<4:17:08,  1.11s/step]INFO 2026-04-07 21:10:48 ot_train.py:439 step:16K smpl:129K ep:155 epch:38.72 loss:0.213 grdn:4.863 lr:1.0e-05 updt_s:0.123 data_s:0.831
Training:  31%|███       | 6160/20000 [1:34:54<3:55:19,  1.02s/step]INFO 2026-04-07 21:11:07 ot_train.py:439 step:16K smpl:129K ep:155 epch:38.76 loss:0.216 grdn:5.454 lr:1.0e-05 updt_s:0.123 data_s:0.819
Training:  31%|███       | 6180/20000 [1:35:13<3:46:50,  1.02step/s]INFO 2026-04-07 21:11:26 ot_train.py:439 step:16K smpl:129K ep:155 epch:38.81 loss:0.208 grdn:5.536 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  31%|███       | 6200/20000 [1:35:31<3:26:59,  1.11step/s]INFO 2026-04-07 21:11:44 ot_train.py:439 step:16K smpl:130K ep:155 epch:38.86 loss:0.212 grdn:5.828 lr:1.0e-05 updt_s:0.124 data_s:0.792
Training:  31%|███       | 6220/20000 [1:35:49<3:07:48,  1.22step/s]INFO 2026-04-07 21:12:02 ot_train.py:439 step:16K smpl:130K ep:156 epch:38.91 loss:0.223 grdn:5.776 lr:1.0e-05 updt_s:0.124 data_s:0.778
Training:  31%|███       | 6240/20000 [1:36:08<3:02:34,  1.26step/s]INFO 2026-04-07 21:12:20 ot_train.py:439 step:16K smpl:130K ep:156 epch:38.96 loss:0.224 grdn:5.448 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  31%|███▏      | 6260/20000 [1:36:29<4:42:44,  1.23s/step]INFO 2026-04-07 21:12:42 ot_train.py:439 step:16K smpl:130K ep:156 epch:39.00 loss:0.219 grdn:4.753 lr:1.0e-05 updt_s:0.124 data_s:0.948
Training:  31%|███▏      | 6280/20000 [1:36:47<3:36:04,  1.06step/s]INFO 2026-04-07 21:13:00 ot_train.py:439 step:16K smpl:130K ep:156 epch:39.05 loss:0.219 grdn:5.270 lr:1.0e-05 updt_s:0.125 data_s:0.762
Training:  32%|███▏      | 6300/20000 [1:37:05<3:13:00,  1.18step/s]INFO 2026-04-07 21:13:18 ot_train.py:439 step:16K smpl:130K ep:156 epch:39.10 loss:0.202 grdn:5.416 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  32%|███▏      | 6320/20000 [1:37:24<3:17:36,  1.15step/s]INFO 2026-04-07 21:13:36 ot_train.py:439 step:16K smpl:131K ep:157 epch:39.15 loss:0.222 grdn:5.076 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  32%|███▏      | 6340/20000 [1:37:42<2:46:22,  1.37step/s]INFO 2026-04-07 21:13:55 ot_train.py:439 step:16K smpl:131K ep:157 epch:39.20 loss:0.212 grdn:4.613 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  32%|███▏      | 6360/20000 [1:38:00<2:44:20,  1.38step/s]INFO 2026-04-07 21:14:13 ot_train.py:439 step:16K smpl:131K ep:157 epch:39.24 loss:0.204 grdn:4.403 lr:1.0e-05 updt_s:0.132 data_s:0.784
Training:  32%|███▏      | 6380/20000 [1:38:19<2:33:50,  1.48step/s]INFO 2026-04-07 21:14:31 ot_train.py:439 step:16K smpl:131K ep:157 epch:39.29 loss:0.214 grdn:4.585 lr:1.0e-05 updt_s:0.123 data_s:0.798
Training:  32%|███▏      | 6400/20000 [1:38:37<2:36:46,  1.45step/s]INFO 2026-04-07 21:14:50 ot_train.py:439 step:16K smpl:131K ep:157 epch:39.34 loss:0.211 grdn:4.193 lr:1.0e-05 updt_s:0.125 data_s:0.797
Training:  32%|███▏      | 6420/20000 [1:38:56<3:02:45,  1.24step/s]INFO 2026-04-07 21:15:09 ot_train.py:439 step:16K smpl:131K ep:158 epch:39.39 loss:0.228 grdn:4.334 lr:1.0e-05 updt_s:0.123 data_s:0.828
Training:  32%|███▏      | 6440/20000 [1:39:15<2:58:12,  1.27step/s]INFO 2026-04-07 21:15:28 ot_train.py:439 step:16K smpl:132K ep:158 epch:39.44 loss:0.209 grdn:4.677 lr:1.0e-05 updt_s:0.122 data_s:0.812
Training:  32%|███▏      | 6460/20000 [1:39:33<3:12:07,  1.17step/s]INFO 2026-04-07 21:15:46 ot_train.py:439 step:16K smpl:132K ep:158 epch:39.48 loss:0.214 grdn:4.623 lr:1.0e-05 updt_s:0.123 data_s:0.785
Training:  32%|███▏      | 6480/20000 [1:39:51<2:50:18,  1.32step/s]INFO 2026-04-07 21:16:04 ot_train.py:439 step:16K smpl:132K ep:158 epch:39.53 loss:0.203 grdn:4.555 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  32%|███▎      | 6500/20000 [1:40:10<2:43:57,  1.37step/s]INFO 2026-04-07 21:16:22 ot_train.py:439 step:16K smpl:132K ep:158 epch:39.58 loss:0.207 grdn:5.332 lr:1.0e-05 updt_s:0.124 data_s:0.785
Training:  33%|███▎      | 6520/20000 [1:40:29<2:51:51,  1.31step/s]INFO 2026-04-07 21:16:41 ot_train.py:439 step:17K smpl:132K ep:159 epch:39.63 loss:0.212 grdn:5.105 lr:1.0e-05 updt_s:0.123 data_s:0.829
Training:  33%|███▎      | 6540/20000 [1:40:48<3:04:58,  1.21step/s]INFO 2026-04-07 21:17:00 ot_train.py:439 step:17K smpl:132K ep:159 epch:39.68 loss:0.209 grdn:4.873 lr:1.0e-05 updt_s:0.124 data_s:0.825
Training:  33%|███▎      | 6560/20000 [1:41:06<3:00:50,  1.24step/s]INFO 2026-04-07 21:17:19 ot_train.py:439 step:17K smpl:132K ep:159 epch:39.72 loss:0.210 grdn:5.170 lr:1.0e-05 updt_s:0.122 data_s:0.809
Training:  33%|███▎      | 6580/20000 [1:41:25<3:02:36,  1.22step/s]INFO 2026-04-07 21:17:37 ot_train.py:439 step:17K smpl:133K ep:159 epch:39.77 loss:0.211 grdn:5.635 lr:1.0e-05 updt_s:0.123 data_s:0.800
Training:  33%|███▎      | 6600/20000 [1:41:43<2:35:40,  1.43step/s]INFO 2026-04-07 21:17:56 ot_train.py:439 step:17K smpl:133K ep:159 epch:39.82 loss:0.206 grdn:5.882 lr:1.0e-05 updt_s:0.125 data_s:0.807
Training:  33%|███▎      | 6620/20000 [1:42:02<2:10:56,  1.70step/s]INFO 2026-04-07 21:18:14 ot_train.py:439 step:17K smpl:133K ep:159 epch:39.87 loss:0.217 grdn:5.731 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:  33%|███▎      | 6640/20000 [1:42:19<2:09:15,  1.72step/s]INFO 2026-04-07 21:18:32 ot_train.py:439 step:17K smpl:133K ep:160 epch:39.92 loss:0.209 grdn:4.493 lr:1.0e-05 updt_s:0.124 data_s:0.773
Training:  33%|███▎      | 6660/20000 [1:42:38<2:16:01,  1.63step/s]INFO 2026-04-07 21:18:50 ot_train.py:439 step:17K smpl:133K ep:160 epch:39.96 loss:0.225 grdn:5.526 lr:1.0e-05 updt_s:0.124 data_s:0.792
Training:  33%|███▎      | 6680/20000 [1:43:00<5:22:18,  1.45s/step]INFO 2026-04-07 21:19:12 ot_train.py:439 step:17K smpl:133K ep:160 epch:40.01 loss:0.214 grdn:5.121 lr:1.0e-05 updt_s:0.124 data_s:0.972
Training:  34%|███▎      | 6700/20000 [1:43:19<5:23:22,  1.46s/step]INFO 2026-04-07 21:19:31 ot_train.py:439 step:17K smpl:134K ep:160 epch:40.06 loss:0.219 grdn:5.698 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  34%|███▎      | 6720/20000 [1:43:38<5:12:08,  1.41s/step]INFO 2026-04-07 21:19:50 ot_train.py:439 step:17K smpl:134K ep:160 epch:40.11 loss:0.211 grdn:5.231 lr:1.0e-05 updt_s:0.125 data_s:0.822
Training:  34%|███▎      | 6740/20000 [1:43:56<5:10:13,  1.40s/step]INFO 2026-04-07 21:20:09 ot_train.py:439 step:17K smpl:134K ep:161 epch:40.16 loss:0.219 grdn:5.418 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  34%|███▍      | 6760/20000 [1:44:14<4:59:40,  1.36s/step]INFO 2026-04-07 21:20:27 ot_train.py:439 step:17K smpl:134K ep:161 epch:40.20 loss:0.209 grdn:4.569 lr:1.0e-05 updt_s:0.123 data_s:0.795
Training:  34%|███▍      | 6780/20000 [1:44:33<5:12:13,  1.42s/step]INFO 2026-04-07 21:20:46 ot_train.py:439 step:17K smpl:134K ep:161 epch:40.25 loss:0.216 grdn:5.178 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  34%|███▍      | 6800/20000 [1:44:52<5:04:11,  1.38s/step]INFO 2026-04-07 21:21:04 ot_train.py:439 step:17K smpl:134K ep:161 epch:40.30 loss:0.208 grdn:4.956 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  34%|███▍      | 6820/20000 [1:45:10<4:50:37,  1.32s/step]INFO 2026-04-07 21:21:23 ot_train.py:439 step:17K smpl:135K ep:161 epch:40.35 loss:0.209 grdn:3.999 lr:1.0e-05 updt_s:0.124 data_s:0.785
Training:  34%|███▍      | 6840/20000 [1:45:28<3:53:40,  1.07s/step]INFO 2026-04-07 21:21:40 ot_train.py:439 step:17K smpl:135K ep:162 epch:40.40 loss:0.208 grdn:5.176 lr:1.0e-05 updt_s:0.124 data_s:0.754
Training:  34%|███▍      | 6860/20000 [1:45:46<4:10:39,  1.14s/step]INFO 2026-04-07 21:21:59 ot_train.py:439 step:17K smpl:135K ep:162 epch:40.44 loss:0.219 grdn:4.913 lr:1.0e-05 updt_s:0.123 data_s:0.793
Training:  34%|███▍      | 6880/20000 [1:46:05<4:50:54,  1.33s/step]INFO 2026-04-07 21:22:17 ot_train.py:439 step:17K smpl:135K ep:162 epch:40.49 loss:0.212 grdn:5.267 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  34%|███▍      | 6900/20000 [1:46:24<5:03:15,  1.39s/step]INFO 2026-04-07 21:22:36 ot_train.py:439 step:17K smpl:135K ep:162 epch:40.54 loss:0.209 grdn:4.461 lr:1.0e-05 updt_s:0.125 data_s:0.812
Training:  35%|███▍      | 6920/20000 [1:46:43<5:12:18,  1.43s/step]INFO 2026-04-07 21:22:55 ot_train.py:439 step:17K smpl:135K ep:162 epch:40.59 loss:0.214 grdn:4.805 lr:1.0e-05 updt_s:0.124 data_s:0.839
Training:  35%|███▍      | 6940/20000 [1:47:01<5:10:33,  1.43s/step]INFO 2026-04-07 21:23:14 ot_train.py:439 step:17K smpl:136K ep:163 epch:40.64 loss:0.202 grdn:4.526 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  35%|███▍      | 6960/20000 [1:47:20<4:58:02,  1.37s/step]INFO 2026-04-07 21:23:33 ot_train.py:439 step:17K smpl:136K ep:163 epch:40.68 loss:0.204 grdn:5.064 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  35%|███▍      | 6980/20000 [1:47:39<5:08:16,  1.42s/step]INFO 2026-04-07 21:23:52 ot_train.py:439 step:17K smpl:136K ep:163 epch:40.73 loss:0.210 grdn:5.113 lr:1.0e-05 updt_s:0.124 data_s:0.821
Training:  35%|███▌      | 7000/20000 [1:47:58<4:59:59,  1.38s/step]INFO 2026-04-07 21:24:11 ot_train.py:439 step:17K smpl:136K ep:163 epch:40.78 loss:0.209 grdn:4.849 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  35%|███▌      | 7020/20000 [1:48:17<5:23:41,  1.50s/step]INFO 2026-04-07 21:24:30 ot_train.py:439 step:17K smpl:136K ep:163 epch:40.83 loss:0.210 grdn:5.243 lr:1.0e-05 updt_s:0.125 data_s:0.811
Training:  35%|███▌      | 7040/20000 [1:48:36<5:13:01,  1.45s/step]INFO 2026-04-07 21:24:48 ot_train.py:439 step:17K smpl:136K ep:164 epch:40.88 loss:0.207 grdn:4.577 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  35%|███▌      | 7060/20000 [1:48:55<5:12:57,  1.45s/step]INFO 2026-04-07 21:25:07 ot_train.py:439 step:17K smpl:136K ep:164 epch:40.92 loss:0.203 grdn:4.381 lr:1.0e-05 updt_s:0.125 data_s:0.836
Training:  35%|███▌      | 7080/20000 [1:49:13<4:55:00,  1.37s/step]INFO 2026-04-07 21:25:26 ot_train.py:439 step:17K smpl:137K ep:164 epch:40.97 loss:0.209 grdn:4.531 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  36%|███▌      | 7100/20000 [1:49:32<2:12:22,  1.62step/s]INFO 2026-04-07 21:25:44 ot_train.py:439 step:17K smpl:137K ep:164 epch:41.02 loss:0.215 grdn:4.555 lr:1.0e-05 updt_s:0.123 data_s:0.795
Training:  36%|███▌      | 7120/20000 [1:49:51<2:01:53,  1.76step/s]INFO 2026-04-07 21:26:04 ot_train.py:439 step:17K smpl:137K ep:164 epch:41.07 loss:0.211 grdn:4.958 lr:1.0e-05 updt_s:0.124 data_s:0.835
Training:  36%|███▌      | 7140/20000 [1:50:09<1:56:09,  1.85step/s]INFO 2026-04-07 21:26:22 ot_train.py:439 step:17K smpl:137K ep:164 epch:41.12 loss:0.211 grdn:5.364 lr:1.0e-05 updt_s:0.124 data_s:0.783
Training:  36%|███▌      | 7160/20000 [1:50:28<1:59:29,  1.79step/s]INFO 2026-04-07 21:26:40 ot_train.py:439 step:17K smpl:137K ep:165 epch:41.16 loss:0.203 grdn:3.893 lr:1.0e-05 updt_s:0.125 data_s:0.794
Training:  36%|███▌      | 7180/20000 [1:50:46<1:57:34,  1.82step/s]INFO 2026-04-07 21:26:59 ot_train.py:439 step:17K smpl:137K ep:165 epch:41.21 loss:0.210 grdn:4.315 lr:1.0e-05 updt_s:0.124 data_s:0.794
Training:  36%|███▌      | 7200/20000 [1:51:05<2:02:45,  1.74step/s]INFO 2026-04-07 21:27:18 ot_train.py:439 step:17K smpl:138K ep:165 epch:41.26 loss:0.208 grdn:5.496 lr:1.0e-05 updt_s:0.125 data_s:0.828
Training:  36%|███▌      | 7220/20000 [1:51:24<1:58:57,  1.79step/s]INFO 2026-04-07 21:27:37 ot_train.py:439 step:17K smpl:138K ep:165 epch:41.31 loss:0.202 grdn:5.406 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  36%|███▌      | 7240/20000 [1:51:43<1:56:27,  1.83step/s]INFO 2026-04-07 21:27:56 ot_train.py:439 step:17K smpl:138K ep:165 epch:41.36 loss:0.209 grdn:4.946 lr:1.0e-05 updt_s:0.125 data_s:0.818
Training:  36%|███▋      | 7260/20000 [1:52:02<1:58:52,  1.79step/s]INFO 2026-04-07 21:28:14 ot_train.py:439 step:17K smpl:138K ep:166 epch:41.40 loss:0.207 grdn:5.210 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:  36%|███▋      | 7280/20000 [1:52:20<2:00:39,  1.76step/s]INFO 2026-04-07 21:28:33 ot_train.py:439 step:17K smpl:138K ep:166 epch:41.45 loss:0.212 grdn:5.116 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  36%|███▋      | 7300/20000 [1:52:39<2:03:17,  1.72step/s]INFO 2026-04-07 21:28:52 ot_train.py:439 step:17K smpl:138K ep:166 epch:41.50 loss:0.204 grdn:4.652 lr:1.0e-05 updt_s:0.125 data_s:0.829
Training:  37%|███▋      | 7320/20000 [1:52:58<1:58:01,  1.79step/s]INFO 2026-04-07 21:29:10 ot_train.py:439 step:17K smpl:139K ep:166 epch:41.55 loss:0.205 grdn:4.540 lr:1.0e-05 updt_s:0.126 data_s:0.797
Training:  37%|███▋      | 7340/20000 [1:53:16<1:53:47,  1.85step/s]INFO 2026-04-07 21:29:28 ot_train.py:439 step:17K smpl:139K ep:166 epch:41.60 loss:0.213 grdn:5.131 lr:1.0e-05 updt_s:0.124 data_s:0.770
Training:  37%|███▋      | 7360/20000 [1:53:35<2:06:31,  1.66step/s]INFO 2026-04-07 21:29:47 ot_train.py:439 step:17K smpl:139K ep:167 epch:41.64 loss:0.202 grdn:4.699 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  37%|███▋      | 7380/20000 [1:53:54<2:03:29,  1.70step/s]INFO 2026-04-07 21:30:07 ot_train.py:439 step:17K smpl:139K ep:167 epch:41.69 loss:0.218 grdn:4.639 lr:1.0e-05 updt_s:0.124 data_s:0.838
Training:  37%|███▋      | 7400/20000 [1:54:12<1:53:45,  1.85step/s]INFO 2026-04-07 21:30:25 ot_train.py:439 step:17K smpl:139K ep:167 epch:41.74 loss:0.204 grdn:4.759 lr:1.0e-05 updt_s:0.125 data_s:0.798
Training:  37%|███▋      | 7420/20000 [1:54:30<1:54:33,  1.83step/s]INFO 2026-04-07 21:30:43 ot_train.py:439 step:17K smpl:139K ep:167 epch:41.79 loss:0.198 grdn:4.791 lr:1.0e-05 updt_s:0.124 data_s:0.775
Training:  37%|███▋      | 7440/20000 [1:54:49<2:01:47,  1.72step/s]INFO 2026-04-07 21:31:02 ot_train.py:439 step:17K smpl:140K ep:167 epch:41.84 loss:0.207 grdn:4.653 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  37%|███▋      | 7460/20000 [1:55:08<1:57:22,  1.78step/s]INFO 2026-04-07 21:31:21 ot_train.py:439 step:17K smpl:140K ep:168 epch:41.88 loss:0.210 grdn:4.876 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  37%|███▋      | 7480/20000 [1:55:27<2:02:36,  1.70step/s]INFO 2026-04-07 21:31:40 ot_train.py:439 step:17K smpl:140K ep:168 epch:41.93 loss:0.214 grdn:4.869 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:  38%|███▊      | 7500/20000 [1:55:46<1:58:38,  1.76step/s]INFO 2026-04-07 21:31:59 ot_train.py:439 step:18K smpl:140K ep:168 epch:41.98 loss:0.205 grdn:4.352 lr:1.0e-05 updt_s:0.125 data_s:0.823
Training:  38%|███▊      | 7520/20000 [1:56:07<2:51:41,  1.21step/s]INFO 2026-04-07 21:32:20 ot_train.py:439 step:18K smpl:140K ep:168 epch:42.03 loss:0.208 grdn:4.465 lr:1.0e-05 updt_s:0.122 data_s:0.939
Training:  38%|███▊      | 7540/20000 [1:56:26<2:43:06,  1.27step/s]INFO 2026-04-07 21:32:39 ot_train.py:439 step:18K smpl:140K ep:168 epch:42.07 loss:0.204 grdn:4.367 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  38%|███▊      | 7560/20000 [1:56:45<2:35:39,  1.33step/s]INFO 2026-04-07 21:32:58 ot_train.py:439 step:18K smpl:140K ep:168 epch:42.12 loss:0.199 grdn:4.042 lr:1.0e-05 updt_s:0.125 data_s:0.816
Training:  38%|███▊      | 7580/20000 [1:57:04<2:31:32,  1.37step/s]INFO 2026-04-07 21:33:16 ot_train.py:439 step:18K smpl:141K ep:169 epch:42.17 loss:0.212 grdn:4.398 lr:1.0e-05 updt_s:0.125 data_s:0.798
Training:  38%|███▊      | 7600/20000 [1:57:23<2:35:21,  1.33step/s]INFO 2026-04-07 21:33:35 ot_train.py:439 step:18K smpl:141K ep:169 epch:42.22 loss:0.202 grdn:4.589 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  38%|███▊      | 7620/20000 [1:57:42<2:36:04,  1.32step/s]INFO 2026-04-07 21:33:54 ot_train.py:439 step:18K smpl:141K ep:169 epch:42.27 loss:0.211 grdn:4.828 lr:1.0e-05 updt_s:0.124 data_s:0.827
Training:  38%|███▊      | 7640/20000 [1:58:00<2:30:44,  1.37step/s]INFO 2026-04-07 21:34:13 ot_train.py:439 step:18K smpl:141K ep:169 epch:42.31 loss:0.198 grdn:5.289 lr:1.0e-05 updt_s:0.134 data_s:0.799
Training:  38%|███▊      | 7660/20000 [1:58:19<2:32:06,  1.35step/s]INFO 2026-04-07 21:34:32 ot_train.py:439 step:18K smpl:141K ep:169 epch:42.36 loss:0.202 grdn:5.028 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  38%|███▊      | 7680/20000 [1:58:38<2:37:03,  1.31step/s]INFO 2026-04-07 21:34:51 ot_train.py:439 step:18K smpl:141K ep:170 epch:42.41 loss:0.207 grdn:4.892 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  38%|███▊      | 7700/20000 [1:58:57<2:36:24,  1.31step/s]INFO 2026-04-07 21:35:09 ot_train.py:439 step:18K smpl:142K ep:170 epch:42.46 loss:0.212 grdn:4.803 lr:1.0e-05 updt_s:0.123 data_s:0.809
Training:  39%|███▊      | 7720/20000 [1:59:14<2:27:11,  1.39step/s]INFO 2026-04-07 21:35:27 ot_train.py:439 step:18K smpl:142K ep:170 epch:42.51 loss:0.215 grdn:5.083 lr:1.0e-05 updt_s:0.125 data_s:0.757
Training:  39%|███▊      | 7740/20000 [1:59:33<2:38:47,  1.29step/s]INFO 2026-04-07 21:35:46 ot_train.py:439 step:18K smpl:142K ep:170 epch:42.55 loss:0.206 grdn:5.368 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:  39%|███▉      | 7760/20000 [1:59:52<2:29:17,  1.37step/s]INFO 2026-04-07 21:36:05 ot_train.py:439 step:18K smpl:142K ep:170 epch:42.60 loss:0.219 grdn:5.261 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  39%|███▉      | 7780/20000 [2:00:11<2:39:23,  1.28step/s]INFO 2026-04-07 21:36:24 ot_train.py:439 step:18K smpl:142K ep:171 epch:42.65 loss:0.211 grdn:4.781 lr:1.0e-05 updt_s:0.125 data_s:0.826
Training:  39%|███▉      | 7800/20000 [2:00:30<2:31:15,  1.34step/s]INFO 2026-04-07 21:36:42 ot_train.py:439 step:18K smpl:142K ep:171 epch:42.70 loss:0.200 grdn:4.300 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  39%|███▉      | 7820/20000 [2:00:48<2:35:45,  1.30step/s]INFO 2026-04-07 21:37:01 ot_train.py:439 step:18K smpl:143K ep:171 epch:42.75 loss:0.202 grdn:4.714 lr:1.0e-05 updt_s:0.125 data_s:0.809
Training:  39%|███▉      | 7840/20000 [2:01:07<2:28:09,  1.37step/s]INFO 2026-04-07 21:37:20 ot_train.py:439 step:18K smpl:143K ep:171 epch:42.79 loss:0.207 grdn:4.593 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  39%|███▉      | 7860/20000 [2:01:25<2:32:48,  1.32step/s]INFO 2026-04-07 21:37:38 ot_train.py:439 step:18K smpl:143K ep:171 epch:42.84 loss:0.201 grdn:4.672 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:  39%|███▉      | 7880/20000 [2:01:44<2:40:22,  1.26step/s]INFO 2026-04-07 21:37:57 ot_train.py:439 step:18K smpl:143K ep:172 epch:42.89 loss:0.210 grdn:4.487 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  40%|███▉      | 7900/20000 [2:02:03<2:31:13,  1.33step/s]INFO 2026-04-07 21:38:16 ot_train.py:439 step:18K smpl:143K ep:172 epch:42.94 loss:0.204 grdn:4.144 lr:1.0e-05 updt_s:0.123 data_s:0.816
Training:  40%|███▉      | 7920/20000 [2:02:21<2:12:42,  1.52step/s]INFO 2026-04-07 21:38:34 ot_train.py:439 step:18K smpl:143K ep:172 epch:42.99 loss:0.201 grdn:4.549 lr:1.0e-05 updt_s:0.124 data_s:0.776
Training:  40%|███▉      | 7940/20000 [2:02:42<3:16:11,  1.02step/s]INFO 2026-04-07 21:38:55 ot_train.py:439 step:18K smpl:144K ep:172 epch:43.03 loss:0.208 grdn:4.932 lr:1.0e-05 updt_s:0.124 data_s:0.937
Training:  40%|███▉      | 7960/20000 [2:03:01<2:59:43,  1.12step/s]INFO 2026-04-07 21:39:13 ot_train.py:439 step:18K smpl:144K ep:172 epch:43.08 loss:0.203 grdn:4.734 lr:1.0e-05 updt_s:0.123 data_s:0.786
Training:  40%|███▉      | 7980/20000 [2:03:19<2:31:27,  1.32step/s]INFO 2026-04-07 21:39:31 ot_train.py:439 step:18K smpl:144K ep:173 epch:43.13 loss:0.209 grdn:4.732 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  40%|████      | 8000/20000 [2:03:37<1:55:25,  1.73step/s]INFO 2026-04-07 21:39:50 ot_train.py:439 step:18K smpl:144K ep:173 epch:43.18 loss:0.206 grdn:4.280 lr:1.0e-05 updt_s:0.124 data_s:0.793
Training:  40%|████      | 8020/20000 [2:03:56<1:56:51,  1.71step/s]INFO 2026-04-07 21:40:09 ot_train.py:439 step:18K smpl:144K ep:173 epch:43.23 loss:0.199 grdn:4.418 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  40%|████      | 8040/20000 [2:04:14<1:51:53,  1.78step/s]INFO 2026-04-07 21:40:27 ot_train.py:439 step:18K smpl:144K ep:173 epch:43.27 loss:0.203 grdn:4.596 lr:1.0e-05 updt_s:0.124 data_s:0.797
Training:  40%|████      | 8060/20000 [2:04:33<1:50:44,  1.80step/s]INFO 2026-04-07 21:40:46 ot_train.py:439 step:18K smpl:144K ep:173 epch:43.32 loss:0.208 grdn:4.297 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  40%|████      | 8080/20000 [2:04:53<1:57:33,  1.69step/s]INFO 2026-04-07 21:41:05 ot_train.py:439 step:18K smpl:145K ep:173 epch:43.37 loss:0.202 grdn:4.798 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  40%|████      | 8100/20000 [2:05:11<1:49:32,  1.81step/s]INFO 2026-04-07 21:41:24 ot_train.py:439 step:18K smpl:145K ep:174 epch:43.42 loss:0.206 grdn:4.895 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  41%|████      | 8120/20000 [2:05:30<1:47:34,  1.84step/s]INFO 2026-04-07 21:41:42 ot_train.py:439 step:18K smpl:145K ep:174 epch:43.47 loss:0.202 grdn:5.566 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  41%|████      | 8140/20000 [2:05:49<1:50:46,  1.78step/s]INFO 2026-04-07 21:42:01 ot_train.py:439 step:18K smpl:145K ep:174 epch:43.51 loss:0.195 grdn:4.544 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  41%|████      | 8160/20000 [2:06:07<1:46:55,  1.85step/s]INFO 2026-04-07 21:42:19 ot_train.py:439 step:18K smpl:145K ep:174 epch:43.56 loss:0.201 grdn:4.721 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  41%|████      | 8180/20000 [2:06:26<1:52:48,  1.75step/s]INFO 2026-04-07 21:42:38 ot_train.py:439 step:18K smpl:145K ep:174 epch:43.61 loss:0.202 grdn:4.516 lr:1.0e-05 updt_s:0.124 data_s:0.817
Training:  41%|████      | 8200/20000 [2:06:44<1:52:35,  1.75step/s]INFO 2026-04-07 21:42:57 ot_train.py:439 step:18K smpl:146K ep:175 epch:43.66 loss:0.209 grdn:5.750 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  41%|████      | 8220/20000 [2:07:03<1:50:01,  1.78step/s]INFO 2026-04-07 21:43:16 ot_train.py:439 step:18K smpl:146K ep:175 epch:43.71 loss:0.203 grdn:4.629 lr:1.0e-05 updt_s:0.125 data_s:0.821
Training:  41%|████      | 8240/20000 [2:07:22<1:52:41,  1.74step/s]INFO 2026-04-07 21:43:34 ot_train.py:439 step:18K smpl:146K ep:175 epch:43.75 loss:0.206 grdn:4.298 lr:1.0e-05 updt_s:0.124 data_s:0.793
Training:  41%|████▏     | 8260/20000 [2:07:40<1:52:16,  1.74step/s]INFO 2026-04-07 21:43:53 ot_train.py:439 step:18K smpl:146K ep:175 epch:43.80 loss:0.196 grdn:4.262 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  41%|████▏     | 8280/20000 [2:07:59<1:55:53,  1.69step/s]INFO 2026-04-07 21:44:12 ot_train.py:439 step:18K smpl:146K ep:175 epch:43.85 loss:0.207 grdn:5.478 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  42%|████▏     | 8300/20000 [2:08:18<2:07:34,  1.53step/s]INFO 2026-04-07 21:44:31 ot_train.py:439 step:18K smpl:146K ep:176 epch:43.90 loss:0.213 grdn:4.766 lr:1.0e-05 updt_s:0.123 data_s:0.815
Training:  42%|████▏     | 8320/20000 [2:08:36<2:12:31,  1.47step/s]INFO 2026-04-07 21:44:49 ot_train.py:439 step:18K smpl:147K ep:176 epch:43.95 loss:0.211 grdn:4.468 lr:1.0e-05 updt_s:0.123 data_s:0.801
Training:  42%|████▏     | 8340/20000 [2:08:54<1:57:00,  1.66step/s]INFO 2026-04-07 21:45:07 ot_train.py:439 step:18K smpl:147K ep:176 epch:43.99 loss:0.202 grdn:4.638 lr:1.0e-05 updt_s:0.122 data_s:0.771
Training:  42%|████▏     | 8360/20000 [2:09:17<4:20:07,  1.34s/step]INFO 2026-04-07 21:45:29 ot_train.py:439 step:18K smpl:147K ep:176 epch:44.04 loss:0.204 grdn:5.401 lr:1.0e-05 updt_s:0.125 data_s:0.993
Training:  42%|████▏     | 8380/20000 [2:09:35<4:16:46,  1.33s/step]INFO 2026-04-07 21:45:48 ot_train.py:439 step:18K smpl:147K ep:176 epch:44.09 loss:0.197 grdn:4.671 lr:1.0e-05 updt_s:0.125 data_s:0.785
Training:  42%|████▏     | 8400/20000 [2:09:53<4:14:24,  1.32s/step]INFO 2026-04-07 21:46:05 ot_train.py:439 step:18K smpl:147K ep:177 epch:44.14 loss:0.204 grdn:4.820 lr:1.0e-05 updt_s:0.124 data_s:0.761
Training:  42%|████▏     | 8420/20000 [2:10:10<3:26:21,  1.07s/step]INFO 2026-04-07 21:46:23 ot_train.py:439 step:18K smpl:147K ep:177 epch:44.19 loss:0.211 grdn:4.905 lr:1.0e-05 updt_s:0.124 data_s:0.752
Training:  42%|████▏     | 8440/20000 [2:10:28<2:42:38,  1.18step/s]INFO 2026-04-07 21:46:40 ot_train.py:439 step:18K smpl:148K ep:177 epch:44.23 loss:0.202 grdn:4.988 lr:1.0e-05 updt_s:0.123 data_s:0.759
Training:  42%|████▏     | 8460/20000 [2:10:46<2:04:56,  1.54step/s]INFO 2026-04-07 21:46:58 ot_train.py:439 step:18K smpl:148K ep:177 epch:44.28 loss:0.200 grdn:4.916 lr:1.0e-05 updt_s:0.124 data_s:0.777
Training:  42%|████▏     | 8480/20000 [2:11:04<1:52:03,  1.71step/s]INFO 2026-04-07 21:47:17 ot_train.py:439 step:18K smpl:148K ep:177 epch:44.33 loss:0.198 grdn:4.674 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:  42%|████▎     | 8500/20000 [2:11:23<1:47:25,  1.78step/s]INFO 2026-04-07 21:47:36 ot_train.py:439 step:18K smpl:148K ep:178 epch:44.38 loss:0.204 grdn:4.605 lr:1.0e-05 updt_s:0.123 data_s:0.809
Training:  43%|████▎     | 8520/20000 [2:11:42<1:53:18,  1.69step/s]INFO 2026-04-07 21:47:54 ot_train.py:439 step:19K smpl:148K ep:178 epch:44.43 loss:0.202 grdn:4.383 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  43%|████▎     | 8540/20000 [2:12:01<1:50:42,  1.73step/s]INFO 2026-04-07 21:48:14 ot_train.py:439 step:19K smpl:148K ep:178 epch:44.47 loss:0.205 grdn:4.664 lr:1.0e-05 updt_s:0.124 data_s:0.852
Training:  43%|████▎     | 8560/20000 [2:12:21<1:52:43,  1.69step/s]INFO 2026-04-07 21:48:33 ot_train.py:439 step:19K smpl:148K ep:178 epch:44.52 loss:0.197 grdn:5.047 lr:1.0e-05 updt_s:0.123 data_s:0.849
Training:  43%|████▎     | 8580/20000 [2:12:39<1:46:56,  1.78step/s]INFO 2026-04-07 21:48:52 ot_train.py:439 step:19K smpl:149K ep:178 epch:44.57 loss:0.210 grdn:5.653 lr:1.0e-05 updt_s:0.125 data_s:0.794
Training:  43%|████▎     | 8600/20000 [2:12:58<1:51:51,  1.70step/s]INFO 2026-04-07 21:49:11 ot_train.py:439 step:19K smpl:149K ep:178 epch:44.62 loss:0.211 grdn:5.259 lr:1.0e-05 updt_s:0.124 data_s:0.823
Training:  43%|████▎     | 8620/20000 [2:13:17<1:51:13,  1.71step/s]INFO 2026-04-07 21:49:30 ot_train.py:439 step:19K smpl:149K ep:179 epch:44.67 loss:0.203 grdn:5.483 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  43%|████▎     | 8640/20000 [2:13:36<1:47:27,  1.76step/s]INFO 2026-04-07 21:49:48 ot_train.py:439 step:19K smpl:149K ep:179 epch:44.71 loss:0.199 grdn:5.386 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:  43%|████▎     | 8660/20000 [2:13:54<1:46:05,  1.78step/s]INFO 2026-04-07 21:50:07 ot_train.py:439 step:19K smpl:149K ep:179 epch:44.76 loss:0.206 grdn:4.910 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  43%|████▎     | 8680/20000 [2:14:13<1:46:34,  1.77step/s]INFO 2026-04-07 21:50:25 ot_train.py:439 step:19K smpl:149K ep:179 epch:44.81 loss:0.195 grdn:4.513 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  44%|████▎     | 8700/20000 [2:14:32<1:45:00,  1.79step/s]INFO 2026-04-07 21:50:44 ot_train.py:439 step:19K smpl:150K ep:179 epch:44.86 loss:0.196 grdn:4.980 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  44%|████▎     | 8720/20000 [2:14:51<1:48:54,  1.73step/s]INFO 2026-04-07 21:51:03 ot_train.py:439 step:19K smpl:150K ep:180 epch:44.91 loss:0.204 grdn:4.964 lr:1.0e-05 updt_s:0.124 data_s:0.830
Training:  44%|████▎     | 8740/20000 [2:15:10<1:43:32,  1.81step/s]INFO 2026-04-07 21:51:22 ot_train.py:439 step:19K smpl:150K ep:180 epch:44.95 loss:0.206 grdn:4.342 lr:1.0e-05 updt_s:0.123 data_s:0.816
Training:  44%|████▍     | 8760/20000 [2:15:29<2:36:37,  1.20step/s]INFO 2026-04-07 21:51:42 ot_train.py:439 step:19K smpl:150K ep:180 epch:45.00 loss:0.206 grdn:4.545 lr:1.0e-05 updt_s:0.123 data_s:0.845
Training:  44%|████▍     | 8780/20000 [2:15:47<1:57:46,  1.59step/s]INFO 2026-04-07 21:52:00 ot_train.py:439 step:19K smpl:150K ep:180 epch:45.05 loss:0.198 grdn:5.204 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  44%|████▍     | 8800/20000 [2:16:06<3:17:26,  1.06s/step]INFO 2026-04-07 21:52:19 ot_train.py:439 step:19K smpl:150K ep:180 epch:45.10 loss:0.202 grdn:4.567 lr:1.0e-05 updt_s:0.123 data_s:0.836
Training:  44%|████▍     | 8820/20000 [2:16:25<3:43:23,  1.20s/step]INFO 2026-04-07 21:52:38 ot_train.py:439 step:19K smpl:151K ep:181 epch:45.15 loss:0.201 grdn:4.787 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  44%|████▍     | 8840/20000 [2:16:44<4:03:24,  1.31s/step]INFO 2026-04-07 21:52:56 ot_train.py:439 step:19K smpl:151K ep:181 epch:45.19 loss:0.200 grdn:4.627 lr:1.0e-05 updt_s:0.125 data_s:0.801
Training:  44%|████▍     | 8860/20000 [2:17:02<4:27:45,  1.44s/step]INFO 2026-04-07 21:53:15 ot_train.py:439 step:19K smpl:151K ep:181 epch:45.24 loss:0.201 grdn:4.786 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  44%|████▍     | 8880/20000 [2:17:21<4:07:57,  1.34s/step]INFO 2026-04-07 21:53:34 ot_train.py:439 step:19K smpl:151K ep:181 epch:45.29 loss:0.203 grdn:4.891 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  44%|████▍     | 8900/20000 [2:17:39<4:05:29,  1.33s/step]INFO 2026-04-07 21:53:52 ot_train.py:439 step:19K smpl:151K ep:181 epch:45.34 loss:0.205 grdn:4.592 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:  45%|████▍     | 8920/20000 [2:17:57<4:15:03,  1.38s/step]INFO 2026-04-07 21:54:10 ot_train.py:439 step:19K smpl:151K ep:182 epch:45.39 loss:0.202 grdn:4.697 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  45%|████▍     | 8940/20000 [2:18:16<4:14:30,  1.38s/step]INFO 2026-04-07 21:54:29 ot_train.py:439 step:19K smpl:152K ep:182 epch:45.43 loss:0.203 grdn:4.474 lr:1.0e-05 updt_s:0.135 data_s:0.806
Training:  45%|████▍     | 8960/20000 [2:18:34<4:18:04,  1.40s/step]INFO 2026-04-07 21:54:47 ot_train.py:439 step:19K smpl:152K ep:182 epch:45.48 loss:0.202 grdn:4.553 lr:1.0e-05 updt_s:0.125 data_s:0.784
Training:  45%|████▍     | 8980/20000 [2:18:53<4:16:43,  1.40s/step]INFO 2026-04-07 21:55:06 ot_train.py:439 step:19K smpl:152K ep:182 epch:45.53 loss:0.209 grdn:4.478 lr:1.0e-05 updt_s:0.123 data_s:0.818
Training:  45%|████▌     | 9000/20000 [2:19:11<3:55:12,  1.28s/step]INFO 2026-04-07 21:55:24 ot_train.py:439 step:19K smpl:152K ep:182 epch:45.58 loss:0.197 grdn:4.817 lr:1.0e-05 updt_s:0.124 data_s:0.771
Training:  45%|████▌     | 9020/20000 [2:19:29<4:17:27,  1.41s/step]INFO 2026-04-07 21:55:42 ot_train.py:439 step:19K smpl:152K ep:183 epch:45.63 loss:0.196 grdn:4.667 lr:1.0e-05 updt_s:0.125 data_s:0.766
Training:  45%|████▌     | 9040/20000 [2:19:47<4:12:48,  1.38s/step]INFO 2026-04-07 21:56:00 ot_train.py:439 step:19K smpl:152K ep:183 epch:45.67 loss:0.196 grdn:4.811 lr:1.0e-05 updt_s:0.125 data_s:0.783
Training:  45%|████▌     | 9060/20000 [2:20:05<4:06:11,  1.35s/step]INFO 2026-04-07 21:56:18 ot_train.py:439 step:19K smpl:152K ep:183 epch:45.72 loss:0.204 grdn:4.682 lr:1.0e-05 updt_s:0.124 data_s:0.783
Training:  45%|████▌     | 9080/20000 [2:20:23<3:57:52,  1.31s/step]INFO 2026-04-07 21:56:36 ot_train.py:439 step:19K smpl:153K ep:183 epch:45.77 loss:0.196 grdn:5.107 lr:1.0e-05 updt_s:0.124 data_s:0.756
Training:  46%|████▌     | 9100/20000 [2:20:41<4:05:48,  1.35s/step]INFO 2026-04-07 21:56:54 ot_train.py:439 step:19K smpl:153K ep:183 epch:45.82 loss:0.200 grdn:4.472 lr:1.0e-05 updt_s:0.125 data_s:0.790
Training:  46%|████▌     | 9120/20000 [2:20:59<4:08:32,  1.37s/step]INFO 2026-04-07 21:57:12 ot_train.py:439 step:19K smpl:153K ep:183 epch:45.87 loss:0.197 grdn:4.774 lr:1.0e-05 updt_s:0.125 data_s:0.778
Training:  46%|████▌     | 9140/20000 [2:21:17<4:02:47,  1.34s/step]INFO 2026-04-07 21:57:30 ot_train.py:439 step:19K smpl:153K ep:184 epch:45.91 loss:0.204 grdn:4.590 lr:1.0e-05 updt_s:0.124 data_s:0.775
Training:  46%|████▌     | 9160/20000 [2:21:36<4:12:04,  1.40s/step]INFO 2026-04-07 21:57:48 ot_train.py:439 step:19K smpl:153K ep:184 epch:45.96 loss:0.192 grdn:4.008 lr:1.0e-05 updt_s:0.125 data_s:0.782
Training:  46%|████▌     | 9180/20000 [2:21:54<2:40:03,  1.13step/s]INFO 2026-04-07 21:58:07 ot_train.py:439 step:19K smpl:153K ep:184 epch:46.01 loss:0.196 grdn:4.059 lr:1.0e-05 updt_s:0.123 data_s:0.809
Training:  46%|████▌     | 9200/20000 [2:22:13<2:09:23,  1.39step/s]INFO 2026-04-07 21:58:25 ot_train.py:439 step:19K smpl:154K ep:184 epch:46.06 loss:0.197 grdn:4.541 lr:1.0e-05 updt_s:0.125 data_s:0.799
Training:  46%|████▌     | 9220/20000 [2:22:31<2:06:17,  1.42step/s]INFO 2026-04-07 21:58:43 ot_train.py:439 step:19K smpl:154K ep:184 epch:46.10 loss:0.203 grdn:4.775 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:  46%|████▌     | 9240/20000 [2:22:50<2:29:49,  1.20step/s]INFO 2026-04-07 21:59:03 ot_train.py:439 step:19K smpl:154K ep:185 epch:46.15 loss:0.183 grdn:4.209 lr:1.0e-05 updt_s:0.124 data_s:0.834
Training:  46%|████▋     | 9260/20000 [2:23:09<2:37:28,  1.14step/s]INFO 2026-04-07 21:59:22 ot_train.py:439 step:19K smpl:154K ep:185 epch:46.20 loss:0.205 grdn:5.124 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  46%|████▋     | 9280/20000 [2:23:28<2:38:13,  1.13step/s]INFO 2026-04-07 21:59:40 ot_train.py:439 step:19K smpl:154K ep:185 epch:46.25 loss:0.200 grdn:4.694 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  46%|████▋     | 9300/20000 [2:23:46<2:33:26,  1.16step/s]INFO 2026-04-07 21:59:58 ot_train.py:439 step:19K smpl:154K ep:185 epch:46.30 loss:0.203 grdn:5.297 lr:1.0e-05 updt_s:0.124 data_s:0.776
Training:  47%|████▋     | 9320/20000 [2:24:05<2:49:17,  1.05step/s]INFO 2026-04-07 22:00:17 ot_train.py:439 step:19K smpl:155K ep:185 epch:46.34 loss:0.196 grdn:5.335 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  47%|████▋     | 9340/20000 [2:24:23<2:53:27,  1.02step/s]INFO 2026-04-07 22:00:36 ot_train.py:439 step:19K smpl:155K ep:186 epch:46.39 loss:0.191 grdn:4.726 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  47%|████▋     | 9360/20000 [2:24:42<3:04:32,  1.04s/step]INFO 2026-04-07 22:00:55 ot_train.py:439 step:19K smpl:155K ep:186 epch:46.44 loss:0.192 grdn:4.777 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  47%|████▋     | 9380/20000 [2:25:00<2:49:48,  1.04step/s]INFO 2026-04-07 22:01:13 ot_train.py:439 step:19K smpl:155K ep:186 epch:46.49 loss:0.192 grdn:4.139 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  47%|████▋     | 9400/20000 [2:25:19<3:08:13,  1.07s/step]INFO 2026-04-07 22:01:32 ot_train.py:439 step:19K smpl:155K ep:186 epch:46.54 loss:0.198 grdn:4.672 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  47%|████▋     | 9420/20000 [2:25:38<3:06:03,  1.06s/step]INFO 2026-04-07 22:01:51 ot_train.py:439 step:19K smpl:155K ep:186 epch:46.58 loss:0.206 grdn:4.641 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  47%|████▋     | 9440/20000 [2:25:57<2:57:17,  1.01s/step]INFO 2026-04-07 22:02:09 ot_train.py:439 step:19K smpl:156K ep:187 epch:46.63 loss:0.201 grdn:5.521 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  47%|████▋     | 9460/20000 [2:26:16<3:05:57,  1.06s/step]INFO 2026-04-07 22:02:28 ot_train.py:439 step:19K smpl:156K ep:187 epch:46.68 loss:0.205 grdn:5.023 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  47%|████▋     | 9480/20000 [2:26:35<2:50:29,  1.03step/s]INFO 2026-04-07 22:02:47 ot_train.py:439 step:19K smpl:156K ep:187 epch:46.73 loss:0.191 grdn:5.116 lr:1.0e-05 updt_s:0.125 data_s:0.819
Training:  48%|████▊     | 9500/20000 [2:26:54<3:04:31,  1.05s/step]INFO 2026-04-07 22:03:06 ot_train.py:439 step:20K smpl:156K ep:187 epch:46.78 loss:0.204 grdn:5.235 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  48%|████▊     | 9520/20000 [2:27:12<2:53:55,  1.00step/s]INFO 2026-04-07 22:03:25 ot_train.py:439 step:20K smpl:156K ep:187 epch:46.82 loss:0.205 grdn:5.088 lr:1.0e-05 updt_s:0.125 data_s:0.806
Training:  48%|████▊     | 9540/20000 [2:27:31<2:59:12,  1.03s/step]INFO 2026-04-07 22:03:43 ot_train.py:439 step:20K smpl:156K ep:187 epch:46.87 loss:0.203 grdn:5.287 lr:1.0e-05 updt_s:0.125 data_s:0.807
Training:  48%|████▊     | 9560/20000 [2:27:50<2:53:56,  1.00step/s]INFO 2026-04-07 22:04:03 ot_train.py:439 step:20K smpl:156K ep:188 epch:46.92 loss:0.206 grdn:5.490 lr:1.0e-05 updt_s:0.125 data_s:0.828
Training:  48%|████▊     | 9580/20000 [2:28:09<3:02:57,  1.05s/step]INFO 2026-04-07 22:04:21 ot_train.py:439 step:20K smpl:157K ep:188 epch:46.97 loss:0.196 grdn:5.015 lr:1.0e-05 updt_s:0.126 data_s:0.810
Training:  48%|████▊     | 9600/20000 [2:28:28<3:01:27,  1.05s/step]INFO 2026-04-07 22:04:41 ot_train.py:439 step:20K smpl:157K ep:188 epch:47.02 loss:0.195 grdn:4.657 lr:1.0e-05 updt_s:0.123 data_s:0.838
Training:  48%|████▊     | 9620/20000 [2:28:47<3:07:25,  1.08s/step]INFO 2026-04-07 22:04:59 ot_train.py:439 step:20K smpl:157K ep:188 epch:47.06 loss:0.196 grdn:4.697 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  48%|████▊     | 9640/20000 [2:29:04<2:44:53,  1.05step/s]INFO 2026-04-07 22:05:17 ot_train.py:439 step:20K smpl:157K ep:188 epch:47.11 loss:0.198 grdn:4.811 lr:1.0e-05 updt_s:0.124 data_s:0.760
Training:  48%|████▊     | 9660/20000 [2:29:23<2:51:25,  1.01step/s]INFO 2026-04-07 22:05:35 ot_train.py:439 step:20K smpl:157K ep:189 epch:47.16 loss:0.201 grdn:5.008 lr:1.0e-05 updt_s:0.126 data_s:0.793
Training:  48%|████▊     | 9680/20000 [2:29:41<2:51:48,  1.00step/s]INFO 2026-04-07 22:05:54 ot_train.py:439 step:20K smpl:157K ep:189 epch:47.21 loss:0.190 grdn:4.213 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  48%|████▊     | 9700/20000 [2:30:00<2:55:52,  1.02s/step]INFO 2026-04-07 22:06:13 ot_train.py:439 step:20K smpl:158K ep:189 epch:47.26 loss:0.200 grdn:5.024 lr:1.0e-05 updt_s:0.125 data_s:0.826
Training:  49%|████▊     | 9720/20000 [2:30:19<3:01:04,  1.06s/step]INFO 2026-04-07 22:06:32 ot_train.py:439 step:20K smpl:158K ep:189 epch:47.30 loss:0.196 grdn:4.801 lr:1.0e-05 updt_s:0.125 data_s:0.810
Training:  49%|████▊     | 9740/20000 [2:30:38<2:49:10,  1.01step/s]INFO 2026-04-07 22:06:50 ot_train.py:439 step:20K smpl:158K ep:189 epch:47.35 loss:0.195 grdn:4.836 lr:1.0e-05 updt_s:0.125 data_s:0.803
Training:  49%|████▉     | 9760/20000 [2:30:56<2:44:23,  1.04step/s]INFO 2026-04-07 22:07:09 ot_train.py:439 step:20K smpl:158K ep:190 epch:47.40 loss:0.193 grdn:4.968 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  49%|████▉     | 9780/20000 [2:31:14<2:49:49,  1.00step/s]INFO 2026-04-07 22:07:27 ot_train.py:439 step:20K smpl:158K ep:190 epch:47.45 loss:0.188 grdn:4.064 lr:1.0e-05 updt_s:0.125 data_s:0.804
Training:  49%|████▉     | 9800/20000 [2:31:32<2:45:48,  1.03step/s]INFO 2026-04-07 22:07:45 ot_train.py:439 step:20K smpl:158K ep:190 epch:47.50 loss:0.203 grdn:5.074 lr:1.0e-05 updt_s:0.124 data_s:0.774
Training:  49%|████▉     | 9820/20000 [2:31:50<2:42:58,  1.04step/s]INFO 2026-04-07 22:08:03 ot_train.py:439 step:20K smpl:159K ep:190 epch:47.54 loss:0.194 grdn:4.893 lr:1.0e-05 updt_s:0.125 data_s:0.776
Training:  49%|████▉     | 9840/20000 [2:32:09<2:52:32,  1.02s/step]INFO 2026-04-07 22:08:22 ot_train.py:439 step:20K smpl:159K ep:190 epch:47.59 loss:0.203 grdn:4.510 lr:1.0e-05 updt_s:0.125 data_s:0.800
Training:  49%|████▉     | 9860/20000 [2:32:27<2:47:53,  1.01step/s]INFO 2026-04-07 22:08:40 ot_train.py:439 step:20K smpl:159K ep:191 epch:47.64 loss:0.202 grdn:4.407 lr:1.0e-05 updt_s:0.125 data_s:0.783
Training:  49%|████▉     | 9880/20000 [2:32:46<3:03:39,  1.09s/step]INFO 2026-04-07 22:08:59 ot_train.py:439 step:20K smpl:159K ep:191 epch:47.69 loss:0.191 grdn:4.404 lr:1.0e-05 updt_s:0.126 data_s:0.827
Training:  50%|████▉     | 9900/20000 [2:33:05<3:30:26,  1.25s/step]INFO 2026-04-07 22:09:18 ot_train.py:439 step:20K smpl:159K ep:191 epch:47.74 loss:0.200 grdn:4.857 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  50%|████▉     | 9920/20000 [2:33:24<3:42:57,  1.33s/step]INFO 2026-04-07 22:09:37 ot_train.py:439 step:20K smpl:159K ep:191 epch:47.78 loss:0.191 grdn:5.192 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  50%|████▉     | 9940/20000 [2:33:42<3:19:49,  1.19s/step]INFO 2026-04-07 22:09:55 ot_train.py:439 step:20K smpl:160K ep:191 epch:47.83 loss:0.195 grdn:4.641 lr:1.0e-05 updt_s:0.124 data_s:0.779
Training:  50%|████▉     | 9960/20000 [2:34:01<3:29:47,  1.25s/step]INFO 2026-04-07 22:10:13 ot_train.py:439 step:20K smpl:160K ep:192 epch:47.88 loss:0.199 grdn:5.183 lr:1.0e-05 updt_s:0.123 data_s:0.801
Training:  50%|████▉     | 9980/20000 [2:34:19<3:18:21,  1.19s/step]INFO 2026-04-07 22:10:32 ot_train.py:439 step:20K smpl:160K ep:192 epch:47.93 loss:0.202 grdn:5.175 lr:1.0e-05 updt_s:0.123 data_s:0.783
Training:  50%|█████     | 10000/20000 [2:34:38<3:36:50,  1.30s/step]INFO 2026-04-07 22:10:50 ot_train.py:439 step:20K smpl:160K ep:192 epch:47.98 loss:0.203 grdn:4.682 lr:1.0e-05 updt_s:0.125 data_s:0.820
INFO 2026-04-07 22:10:50 ot_train.py:459 Checkpoint policy after step 20000
Training:  50%|█████     | 10020/20000 [2:34:57<3:51:55,  1.39s/step]INFO 2026-04-07 22:11:10 ot_train.py:439 step:20K smpl:160K ep:192 epch:48.02 loss:0.192 grdn:4.876 lr:1.0e-05 updt_s:0.125 data_s:0.809
Training:  50%|█████     | 10040/20000 [2:35:16<3:33:16,  1.28s/step]INFO 2026-04-07 22:11:29 ot_train.py:439 step:20K smpl:160K ep:192 epch:48.07 loss:0.194 grdn:4.376 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  50%|█████     | 10060/20000 [2:35:34<3:28:49,  1.26s/step]INFO 2026-04-07 22:11:47 ot_train.py:439 step:20K smpl:160K ep:192 epch:48.12 loss:0.195 grdn:4.340 lr:1.0e-05 updt_s:0.123 data_s:0.786
Training:  50%|█████     | 10080/20000 [2:35:53<3:05:23,  1.12s/step]INFO 2026-04-07 22:12:05 ot_train.py:439 step:20K smpl:161K ep:193 epch:48.17 loss:0.194 grdn:4.459 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  50%|█████     | 10100/20000 [2:36:11<2:37:44,  1.05step/s]INFO 2026-04-07 22:12:23 ot_train.py:439 step:20K smpl:161K ep:193 epch:48.22 loss:0.191 grdn:4.735 lr:1.0e-05 updt_s:0.123 data_s:0.779
Training:  51%|█████     | 10120/20000 [2:36:29<2:45:00,  1.00s/step]INFO 2026-04-07 22:12:42 ot_train.py:439 step:20K smpl:161K ep:193 epch:48.26 loss:0.191 grdn:4.287 lr:1.0e-05 updt_s:0.136 data_s:0.785
Training:  51%|█████     | 10140/20000 [2:36:48<2:41:07,  1.02step/s]INFO 2026-04-07 22:13:00 ot_train.py:439 step:20K smpl:161K ep:193 epch:48.31 loss:0.195 grdn:4.469 lr:1.0e-05 updt_s:0.123 data_s:0.797
Training:  51%|█████     | 10160/20000 [2:37:06<2:38:17,  1.04step/s]INFO 2026-04-07 22:13:19 ot_train.py:439 step:20K smpl:161K ep:193 epch:48.36 loss:0.197 grdn:4.636 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  51%|█████     | 10180/20000 [2:37:26<2:57:49,  1.09s/step]INFO 2026-04-07 22:13:39 ot_train.py:439 step:20K smpl:161K ep:194 epch:48.41 loss:0.197 grdn:4.502 lr:1.0e-05 updt_s:0.124 data_s:0.850
Training:  51%|█████     | 10200/20000 [2:37:45<3:13:06,  1.18s/step]INFO 2026-04-07 22:13:57 ot_train.py:439 step:20K smpl:162K ep:194 epch:48.46 loss:0.196 grdn:4.669 lr:1.0e-05 updt_s:0.123 data_s:0.814
Training:  51%|█████     | 10220/20000 [2:38:03<2:55:01,  1.07s/step]INFO 2026-04-07 22:14:16 ot_train.py:439 step:20K smpl:162K ep:194 epch:48.50 loss:0.186 grdn:4.328 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:  51%|█████     | 10240/20000 [2:38:21<2:41:41,  1.01step/s]INFO 2026-04-07 22:14:34 ot_train.py:439 step:20K smpl:162K ep:194 epch:48.55 loss:0.202 grdn:5.337 lr:1.0e-05 updt_s:0.123 data_s:0.797
Training:  51%|█████▏    | 10260/20000 [2:38:40<2:32:58,  1.06step/s]INFO 2026-04-07 22:14:53 ot_train.py:439 step:20K smpl:162K ep:194 epch:48.60 loss:0.191 grdn:4.264 lr:1.0e-05 updt_s:0.123 data_s:0.805
Training:  51%|█████▏    | 10280/20000 [2:38:58<2:05:33,  1.29step/s]INFO 2026-04-07 22:15:11 ot_train.py:439 step:20K smpl:162K ep:195 epch:48.65 loss:0.195 grdn:4.665 lr:1.0e-05 updt_s:0.123 data_s:0.781
Training:  52%|█████▏    | 10300/20000 [2:39:17<2:09:31,  1.25step/s]INFO 2026-04-07 22:15:29 ot_train.py:439 step:20K smpl:162K ep:195 epch:48.70 loss:0.199 grdn:4.471 lr:1.0e-05 updt_s:0.123 data_s:0.803
Training:  52%|█████▏    | 10320/20000 [2:39:35<2:05:43,  1.28step/s]INFO 2026-04-07 22:15:48 ot_train.py:439 step:20K smpl:163K ep:195 epch:48.74 loss:0.193 grdn:4.460 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  52%|█████▏    | 10340/20000 [2:39:54<1:59:23,  1.35step/s]INFO 2026-04-07 22:16:06 ot_train.py:439 step:20K smpl:163K ep:195 epch:48.79 loss:0.201 grdn:4.839 lr:1.0e-05 updt_s:0.123 data_s:0.816
Training:  52%|█████▏    | 10360/20000 [2:40:13<2:11:34,  1.22step/s]INFO 2026-04-07 22:16:25 ot_train.py:439 step:20K smpl:163K ep:195 epch:48.84 loss:0.196 grdn:4.790 lr:1.0e-05 updt_s:0.123 data_s:0.824
Training:  52%|█████▏    | 10380/20000 [2:40:31<2:13:09,  1.20step/s]INFO 2026-04-07 22:16:44 ot_train.py:439 step:20K smpl:163K ep:196 epch:48.89 loss:0.197 grdn:4.798 lr:1.0e-05 updt_s:0.123 data_s:0.796
Training:  52%|█████▏    | 10400/20000 [2:40:49<1:48:27,  1.48step/s]INFO 2026-04-07 22:17:02 ot_train.py:439 step:20K smpl:163K ep:196 epch:48.94 loss:0.194 grdn:4.250 lr:1.0e-05 updt_s:0.123 data_s:0.766
Training:  52%|█████▏    | 10420/20000 [2:41:08<1:53:45,  1.40step/s]INFO 2026-04-07 22:17:21 ot_train.py:439 step:20K smpl:163K ep:196 epch:48.98 loss:0.194 grdn:4.359 lr:1.0e-05 updt_s:0.124 data_s:0.824
Training:  52%|█████▏    | 10440/20000 [2:41:27<1:30:56,  1.75step/s]INFO 2026-04-07 22:17:40 ot_train.py:439 step:20K smpl:164K ep:196 epch:49.03 loss:0.205 grdn:4.591 lr:1.0e-05 updt_s:0.123 data_s:0.843
Training:  52%|█████▏    | 10460/20000 [2:41:46<1:28:10,  1.80step/s]INFO 2026-04-07 22:17:59 ot_train.py:439 step:20K smpl:164K ep:196 epch:49.08 loss:0.188 grdn:4.249 lr:1.0e-05 updt_s:0.126 data_s:0.809
Training:  52%|█████▏    | 10480/20000 [2:42:04<1:39:20,  1.60step/s]INFO 2026-04-07 22:18:17 ot_train.py:439 step:20K smpl:164K ep:197 epch:49.13 loss:0.199 grdn:4.407 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  52%|█████▎    | 10500/20000 [2:42:23<1:51:26,  1.42step/s]INFO 2026-04-07 22:18:36 ot_train.py:439 step:20K smpl:164K ep:197 epch:49.18 loss:0.194 grdn:4.649 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  53%|█████▎    | 10520/20000 [2:42:42<2:41:28,  1.02s/step]INFO 2026-04-07 22:18:55 ot_train.py:439 step:21K smpl:164K ep:197 epch:49.22 loss:0.191 grdn:4.793 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  53%|█████▎    | 10540/20000 [2:43:01<3:19:49,  1.27s/step]INFO 2026-04-07 22:19:13 ot_train.py:439 step:21K smpl:164K ep:197 epch:49.27 loss:0.187 grdn:4.218 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  53%|█████▎    | 10560/20000 [2:43:20<3:42:01,  1.41s/step]INFO 2026-04-07 22:19:32 ot_train.py:439 step:21K smpl:164K ep:197 epch:49.32 loss:0.197 grdn:5.273 lr:1.0e-05 updt_s:0.123 data_s:0.824
Training:  53%|█████▎    | 10580/20000 [2:43:38<3:35:19,  1.37s/step]INFO 2026-04-07 22:19:51 ot_train.py:439 step:21K smpl:165K ep:197 epch:49.37 loss:0.192 grdn:3.948 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  53%|█████▎    | 10600/20000 [2:43:57<3:44:52,  1.44s/step]INFO 2026-04-07 22:20:09 ot_train.py:439 step:21K smpl:165K ep:198 epch:49.42 loss:0.199 grdn:4.935 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  53%|█████▎    | 10620/20000 [2:44:15<3:45:47,  1.44s/step]INFO 2026-04-07 22:20:28 ot_train.py:439 step:21K smpl:165K ep:198 epch:49.46 loss:0.196 grdn:5.047 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  53%|█████▎    | 10640/20000 [2:44:34<3:31:41,  1.36s/step]INFO 2026-04-07 22:20:46 ot_train.py:439 step:21K smpl:165K ep:198 epch:49.51 loss:0.190 grdn:5.133 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  53%|█████▎    | 10660/20000 [2:44:52<3:30:45,  1.35s/step]INFO 2026-04-07 22:21:04 ot_train.py:439 step:21K smpl:165K ep:198 epch:49.56 loss:0.192 grdn:4.459 lr:1.0e-05 updt_s:0.124 data_s:0.773
Training:  53%|█████▎    | 10680/20000 [2:45:10<3:26:57,  1.33s/step]INFO 2026-04-07 22:21:23 ot_train.py:439 step:21K smpl:165K ep:198 epch:49.61 loss:0.196 grdn:4.577 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  54%|█████▎    | 10700/20000 [2:45:29<3:31:24,  1.36s/step]INFO 2026-04-07 22:21:41 ot_train.py:439 step:21K smpl:166K ep:199 epch:49.66 loss:0.187 grdn:4.581 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:  54%|█████▎    | 10720/20000 [2:45:47<3:44:16,  1.45s/step]INFO 2026-04-07 22:22:00 ot_train.py:439 step:21K smpl:166K ep:199 epch:49.70 loss:0.193 grdn:4.930 lr:1.0e-05 updt_s:0.125 data_s:0.793
Training:  54%|█████▎    | 10740/20000 [2:46:06<3:26:23,  1.34s/step]INFO 2026-04-07 22:22:18 ot_train.py:439 step:21K smpl:166K ep:199 epch:49.75 loss:0.188 grdn:4.588 lr:1.0e-05 updt_s:0.123 data_s:0.806
Training:  54%|█████▍    | 10760/20000 [2:46:24<3:27:38,  1.35s/step]INFO 2026-04-07 22:22:37 ot_train.py:439 step:21K smpl:166K ep:199 epch:49.80 loss:0.186 grdn:4.935 lr:1.0e-05 updt_s:0.124 data_s:0.794
Training:  54%|█████▍    | 10780/20000 [2:46:43<3:26:00,  1.34s/step]INFO 2026-04-07 22:22:55 ot_train.py:439 step:21K smpl:166K ep:199 epch:49.85 loss:0.198 grdn:4.744 lr:1.0e-05 updt_s:0.126 data_s:0.794
Training:  54%|█████▍    | 10800/20000 [2:47:01<3:42:16,  1.45s/step]INFO 2026-04-07 22:23:14 ot_train.py:439 step:21K smpl:166K ep:200 epch:49.90 loss:0.195 grdn:4.399 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  54%|█████▍    | 10820/20000 [2:47:20<3:37:13,  1.42s/step]INFO 2026-04-07 22:23:33 ot_train.py:439 step:21K smpl:167K ep:200 epch:49.94 loss:0.194 grdn:4.368 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  54%|█████▍    | 10840/20000 [2:47:37<2:57:39,  1.16s/step]INFO 2026-04-07 22:23:50 ot_train.py:439 step:21K smpl:167K ep:200 epch:49.99 loss:0.198 grdn:4.708 lr:1.0e-05 updt_s:0.124 data_s:0.734
Training:  54%|█████▍    | 10860/20000 [2:47:57<1:57:17,  1.30step/s]INFO 2026-04-07 22:24:10 ot_train.py:439 step:21K smpl:167K ep:200 epch:50.04 loss:0.195 grdn:4.991 lr:1.0e-05 updt_s:0.124 data_s:0.864
Training:  54%|█████▍    | 10880/20000 [2:48:16<1:57:14,  1.30step/s]INFO 2026-04-07 22:24:29 ot_train.py:439 step:21K smpl:167K ep:200 epch:50.09 loss:0.189 grdn:4.620 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  55%|█████▍    | 10900/20000 [2:48:34<1:56:26,  1.30step/s]INFO 2026-04-07 22:24:47 ot_train.py:439 step:21K smpl:167K ep:201 epch:50.13 loss:0.194 grdn:4.802 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  55%|█████▍    | 10920/20000 [2:48:54<2:02:12,  1.24step/s]INFO 2026-04-07 22:25:07 ot_train.py:439 step:21K smpl:167K ep:201 epch:50.18 loss:0.189 grdn:4.589 lr:1.0e-05 updt_s:0.125 data_s:0.854
Training:  55%|█████▍    | 10940/20000 [2:49:11<1:48:41,  1.39step/s]INFO 2026-04-07 22:25:24 ot_train.py:439 step:21K smpl:168K ep:201 epch:50.23 loss:0.196 grdn:5.433 lr:1.0e-05 updt_s:0.125 data_s:0.740
Training:  55%|█████▍    | 10960/20000 [2:49:30<1:56:27,  1.29step/s]INFO 2026-04-07 22:25:43 ot_train.py:439 step:21K smpl:168K ep:201 epch:50.28 loss:0.185 grdn:4.659 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  55%|█████▍    | 10980/20000 [2:49:49<1:56:19,  1.29step/s]INFO 2026-04-07 22:26:02 ot_train.py:439 step:21K smpl:168K ep:201 epch:50.33 loss:0.191 grdn:4.731 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  55%|█████▌    | 11000/20000 [2:50:08<1:50:39,  1.36step/s]INFO 2026-04-07 22:26:21 ot_train.py:439 step:21K smpl:168K ep:201 epch:50.37 loss:0.193 grdn:5.461 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  55%|█████▌    | 11020/20000 [2:50:27<1:57:03,  1.28step/s]INFO 2026-04-07 22:26:40 ot_train.py:439 step:21K smpl:168K ep:202 epch:50.42 loss:0.199 grdn:4.851 lr:1.0e-05 updt_s:0.124 data_s:0.834
Training:  55%|█████▌    | 11040/20000 [2:50:46<1:51:41,  1.34step/s]INFO 2026-04-07 22:26:58 ot_train.py:439 step:21K smpl:168K ep:202 epch:50.47 loss:0.198 grdn:4.207 lr:1.0e-05 updt_s:0.124 data_s:0.793
Training:  55%|█████▌    | 11060/20000 [2:51:04<1:49:34,  1.36step/s]INFO 2026-04-07 22:27:16 ot_train.py:439 step:21K smpl:168K ep:202 epch:50.52 loss:0.194 grdn:4.446 lr:1.0e-05 updt_s:0.124 data_s:0.783
Training:  55%|█████▌    | 11080/20000 [2:51:22<1:49:49,  1.35step/s]INFO 2026-04-07 22:27:35 ot_train.py:439 step:21K smpl:169K ep:202 epch:50.57 loss:0.188 grdn:4.612 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  56%|█████▌    | 11100/20000 [2:51:41<1:55:31,  1.28step/s]INFO 2026-04-07 22:27:54 ot_train.py:439 step:21K smpl:169K ep:202 epch:50.61 loss:0.187 grdn:4.904 lr:1.0e-05 updt_s:0.124 data_s:0.834
Training:  56%|█████▌    | 11120/20000 [2:52:01<1:55:31,  1.28step/s]INFO 2026-04-07 22:28:13 ot_train.py:439 step:21K smpl:169K ep:203 epch:50.66 loss:0.196 grdn:4.404 lr:1.0e-05 updt_s:0.124 data_s:0.833
Training:  56%|█████▌    | 11140/20000 [2:52:20<1:53:00,  1.31step/s]INFO 2026-04-07 22:28:32 ot_train.py:439 step:21K smpl:169K ep:203 epch:50.71 loss:0.196 grdn:4.183 lr:1.0e-05 updt_s:0.125 data_s:0.831
Training:  56%|█████▌    | 11160/20000 [2:52:39<1:55:45,  1.27step/s]INFO 2026-04-07 22:28:52 ot_train.py:439 step:21K smpl:169K ep:203 epch:50.76 loss:0.187 grdn:4.121 lr:1.0e-05 updt_s:0.125 data_s:0.844
Training:  56%|█████▌    | 11180/20000 [2:52:58<1:51:50,  1.31step/s]INFO 2026-04-07 22:29:11 ot_train.py:439 step:21K smpl:169K ep:203 epch:50.81 loss:0.185 grdn:3.784 lr:1.0e-05 updt_s:0.124 data_s:0.831
Training:  56%|█████▌    | 11200/20000 [2:53:17<1:46:34,  1.38step/s]INFO 2026-04-07 22:29:29 ot_train.py:439 step:21K smpl:170K ep:203 epch:50.85 loss:0.192 grdn:4.168 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  56%|█████▌    | 11220/20000 [2:53:35<1:52:59,  1.30step/s]INFO 2026-04-07 22:29:48 ot_train.py:439 step:21K smpl:170K ep:204 epch:50.90 loss:0.190 grdn:4.786 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  56%|█████▌    | 11240/20000 [2:53:54<1:53:55,  1.28step/s]INFO 2026-04-07 22:30:07 ot_train.py:439 step:21K smpl:170K ep:204 epch:50.95 loss:0.187 grdn:3.987 lr:1.0e-05 updt_s:0.125 data_s:0.820
Training:  56%|█████▋    | 11260/20000 [2:54:16<4:29:59,  1.85s/step]INFO 2026-04-07 22:30:28 ot_train.py:439 step:21K smpl:170K ep:204 epch:51.00 loss:0.198 grdn:4.339 lr:1.0e-05 updt_s:0.122 data_s:0.944
Training:  56%|█████▋    | 11280/20000 [2:54:35<2:31:24,  1.04s/step]INFO 2026-04-07 22:30:47 ot_train.py:439 step:21K smpl:170K ep:204 epch:51.05 loss:0.184 grdn:3.881 lr:1.0e-05 updt_s:0.125 data_s:0.831
Training:  56%|█████▋    | 11300/20000 [2:54:54<2:35:12,  1.07s/step]INFO 2026-04-07 22:31:07 ot_train.py:439 step:21K smpl:170K ep:204 epch:51.09 loss:0.196 grdn:4.186 lr:1.0e-05 updt_s:0.125 data_s:0.831
Training:  57%|█████▋    | 11320/20000 [2:55:12<2:20:24,  1.03step/s]INFO 2026-04-07 22:31:25 ot_train.py:439 step:21K smpl:171K ep:205 epch:51.14 loss:0.183 grdn:4.216 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  57%|█████▋    | 11340/20000 [2:55:31<2:17:52,  1.05step/s]INFO 2026-04-07 22:31:44 ot_train.py:439 step:21K smpl:171K ep:205 epch:51.19 loss:0.189 grdn:4.655 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  57%|█████▋    | 11360/20000 [2:55:50<1:58:41,  1.21step/s]INFO 2026-04-07 22:32:02 ot_train.py:439 step:21K smpl:171K ep:205 epch:51.24 loss:0.197 grdn:4.719 lr:1.0e-05 updt_s:0.123 data_s:0.806
Training:  57%|█████▋    | 11380/20000 [2:56:09<2:05:33,  1.14step/s]INFO 2026-04-07 22:32:21 ot_train.py:439 step:21K smpl:171K ep:205 epch:51.29 loss:0.193 grdn:5.081 lr:1.0e-05 updt_s:0.123 data_s:0.832
Training:  57%|█████▋    | 11400/20000 [2:56:28<2:32:59,  1.07s/step]INFO 2026-04-07 22:32:40 ot_train.py:439 step:21K smpl:171K ep:205 epch:51.33 loss:0.191 grdn:3.856 lr:1.0e-05 updt_s:0.131 data_s:0.824
Training:  57%|█████▋    | 11420/20000 [2:56:47<2:52:11,  1.20s/step]INFO 2026-04-07 22:32:59 ot_train.py:439 step:21K smpl:171K ep:206 epch:51.38 loss:0.195 grdn:4.131 lr:1.0e-05 updt_s:0.122 data_s:0.820
Training:  57%|█████▋    | 11440/20000 [2:57:05<2:49:48,  1.19s/step]INFO 2026-04-07 22:33:18 ot_train.py:439 step:21K smpl:172K ep:206 epch:51.43 loss:0.191 grdn:4.886 lr:1.0e-05 updt_s:0.123 data_s:0.805
Training:  57%|█████▋    | 11460/20000 [2:57:24<3:01:18,  1.27s/step]INFO 2026-04-07 22:33:37 ot_train.py:439 step:21K smpl:172K ep:206 epch:51.48 loss:0.188 grdn:4.372 lr:1.0e-05 updt_s:0.123 data_s:0.832
Training:  57%|█████▋    | 11480/20000 [2:57:44<3:17:33,  1.39s/step]INFO 2026-04-07 22:33:56 ot_train.py:439 step:21K smpl:172K ep:206 epch:51.53 loss:0.188 grdn:5.064 lr:1.0e-05 updt_s:0.124 data_s:0.848
Training:  57%|█████▊    | 11500/20000 [2:58:03<3:19:36,  1.41s/step]INFO 2026-04-07 22:34:16 ot_train.py:439 step:22K smpl:172K ep:206 epch:51.57 loss:0.194 grdn:4.892 lr:1.0e-05 updt_s:0.125 data_s:0.833
Training:  58%|█████▊    | 11520/20000 [2:58:21<3:21:03,  1.42s/step]INFO 2026-04-07 22:34:34 ot_train.py:439 step:22K smpl:172K ep:206 epch:51.62 loss:0.185 grdn:4.660 lr:1.0e-05 updt_s:0.125 data_s:0.795
Training:  58%|█████▊    | 11540/20000 [2:58:40<3:16:12,  1.39s/step]INFO 2026-04-07 22:34:52 ot_train.py:439 step:22K smpl:172K ep:207 epch:51.67 loss:0.191 grdn:4.273 lr:1.0e-05 updt_s:0.125 data_s:0.794
Training:  58%|█████▊    | 11560/20000 [2:58:59<3:19:01,  1.41s/step]INFO 2026-04-07 22:35:11 ot_train.py:439 step:22K smpl:172K ep:207 epch:51.72 loss:0.188 grdn:4.555 lr:1.0e-05 updt_s:0.125 data_s:0.824
Training:  58%|█████▊    | 11580/20000 [2:59:18<3:12:57,  1.38s/step]INFO 2026-04-07 22:35:30 ot_train.py:439 step:22K smpl:173K ep:207 epch:51.77 loss:0.192 grdn:4.968 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  58%|█████▊    | 11600/20000 [2:59:36<3:18:13,  1.42s/step]INFO 2026-04-07 22:35:49 ot_train.py:439 step:22K smpl:173K ep:207 epch:51.81 loss:0.196 grdn:4.765 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:  58%|█████▊    | 11620/20000 [2:59:55<3:14:59,  1.40s/step]INFO 2026-04-07 22:36:07 ot_train.py:439 step:22K smpl:173K ep:207 epch:51.86 loss:0.190 grdn:4.440 lr:1.0e-05 updt_s:0.125 data_s:0.813
Training:  58%|█████▊    | 11640/20000 [3:00:13<3:10:36,  1.37s/step]INFO 2026-04-07 22:36:26 ot_train.py:439 step:22K smpl:173K ep:208 epch:51.91 loss:0.191 grdn:4.463 lr:1.0e-05 updt_s:0.125 data_s:0.792
Training:  58%|█████▊    | 11660/20000 [3:00:32<3:16:47,  1.42s/step]INFO 2026-04-07 22:36:45 ot_train.py:439 step:22K smpl:173K ep:208 epch:51.96 loss:0.187 grdn:4.484 lr:1.0e-05 updt_s:0.125 data_s:0.827
Training:  58%|█████▊    | 11680/20000 [3:00:51<3:36:22,  1.56s/step]INFO 2026-04-07 22:37:04 ot_train.py:439 step:22K smpl:173K ep:208 epch:52.01 loss:0.190 grdn:4.318 lr:1.0e-05 updt_s:0.124 data_s:0.837
Training:  58%|█████▊    | 11700/20000 [3:01:10<3:03:32,  1.33s/step]INFO 2026-04-07 22:37:22 ot_train.py:439 step:22K smpl:174K ep:208 epch:52.05 loss:0.186 grdn:4.402 lr:1.0e-05 updt_s:0.125 data_s:0.791
Training:  59%|█████▊    | 11720/20000 [3:01:28<3:14:33,  1.41s/step]INFO 2026-04-07 22:37:41 ot_train.py:439 step:22K smpl:174K ep:208 epch:52.10 loss:0.187 grdn:4.604 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  59%|█████▊    | 11740/20000 [3:01:47<3:04:45,  1.34s/step]INFO 2026-04-07 22:38:00 ot_train.py:439 step:22K smpl:174K ep:209 epch:52.15 loss:0.192 grdn:4.505 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  59%|█████▉    | 11760/20000 [3:02:06<3:08:55,  1.38s/step]INFO 2026-04-07 22:38:18 ot_train.py:439 step:22K smpl:174K ep:209 epch:52.20 loss:0.187 grdn:4.626 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:  59%|█████▉    | 11780/20000 [3:02:24<3:21:17,  1.47s/step]INFO 2026-04-07 22:38:37 ot_train.py:439 step:22K smpl:174K ep:209 epch:52.25 loss:0.186 grdn:4.635 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  59%|█████▉    | 11800/20000 [3:02:43<3:12:32,  1.41s/step]INFO 2026-04-07 22:38:56 ot_train.py:439 step:22K smpl:174K ep:209 epch:52.29 loss:0.188 grdn:4.161 lr:1.0e-05 updt_s:0.123 data_s:0.812
Training:  59%|█████▉    | 11820/20000 [3:03:01<3:05:44,  1.36s/step]INFO 2026-04-07 22:39:14 ot_train.py:439 step:22K smpl:175K ep:209 epch:52.34 loss:0.184 grdn:4.507 lr:1.0e-05 updt_s:0.125 data_s:0.795
Training:  59%|█████▉    | 11840/20000 [3:03:19<2:55:56,  1.29s/step]INFO 2026-04-07 22:39:32 ot_train.py:439 step:22K smpl:175K ep:210 epch:52.39 loss:0.190 grdn:4.835 lr:1.0e-05 updt_s:0.126 data_s:0.755
Training:  59%|█████▉    | 11860/20000 [3:03:38<3:10:02,  1.40s/step]INFO 2026-04-07 22:39:50 ot_train.py:439 step:22K smpl:175K ep:210 epch:52.44 loss:0.188 grdn:4.667 lr:1.0e-05 updt_s:0.126 data_s:0.803
Training:  59%|█████▉    | 11880/20000 [3:03:56<3:06:38,  1.38s/step]INFO 2026-04-07 22:40:09 ot_train.py:439 step:22K smpl:175K ep:210 epch:52.49 loss:0.192 grdn:5.839 lr:1.0e-05 updt_s:0.127 data_s:0.813
Training:  60%|█████▉    | 11900/20000 [3:04:14<3:00:05,  1.33s/step]INFO 2026-04-07 22:40:27 ot_train.py:439 step:22K smpl:175K ep:210 epch:52.53 loss:0.196 grdn:4.996 lr:1.0e-05 updt_s:0.124 data_s:0.773
Training:  60%|█████▉    | 11920/20000 [3:04:32<2:59:06,  1.33s/step]INFO 2026-04-07 22:40:45 ot_train.py:439 step:22K smpl:175K ep:210 epch:52.58 loss:0.190 grdn:4.133 lr:1.0e-05 updt_s:0.125 data_s:0.753
Training:  60%|█████▉    | 11940/20000 [3:04:50<3:03:37,  1.37s/step]INFO 2026-04-07 22:41:03 ot_train.py:439 step:22K smpl:176K ep:211 epch:52.63 loss:0.189 grdn:4.358 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  60%|█████▉    | 11960/20000 [3:05:08<3:00:32,  1.35s/step]INFO 2026-04-07 22:41:21 ot_train.py:439 step:22K smpl:176K ep:211 epch:52.68 loss:0.190 grdn:4.321 lr:1.0e-05 updt_s:0.126 data_s:0.781
Training:  60%|█████▉    | 11980/20000 [3:05:27<3:02:20,  1.36s/step]INFO 2026-04-07 22:41:40 ot_train.py:439 step:22K smpl:176K ep:211 epch:52.73 loss:0.189 grdn:4.060 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  60%|██████    | 12000/20000 [3:05:46<3:13:00,  1.45s/step]INFO 2026-04-07 22:41:59 ot_train.py:439 step:22K smpl:176K ep:211 epch:52.77 loss:0.185 grdn:4.266 lr:1.0e-05 updt_s:0.123 data_s:0.833
Training:  60%|██████    | 12020/20000 [3:06:04<2:57:15,  1.33s/step]INFO 2026-04-07 22:42:17 ot_train.py:439 step:22K smpl:176K ep:211 epch:52.82 loss:0.189 grdn:4.457 lr:1.0e-05 updt_s:0.126 data_s:0.765
Training:  60%|██████    | 12040/20000 [3:06:22<2:56:36,  1.33s/step]INFO 2026-04-07 22:42:35 ot_train.py:439 step:22K smpl:176K ep:211 epch:52.87 loss:0.189 grdn:4.159 lr:1.0e-05 updt_s:0.126 data_s:0.777
Training:  60%|██████    | 12060/20000 [3:06:40<3:06:14,  1.41s/step]INFO 2026-04-07 22:42:53 ot_train.py:439 step:22K smpl:176K ep:212 epch:52.92 loss:0.183 grdn:3.983 lr:1.0e-05 updt_s:0.124 data_s:0.774
Training:  60%|██████    | 12080/20000 [3:06:58<3:01:19,  1.37s/step]INFO 2026-04-07 22:43:11 ot_train.py:439 step:22K smpl:177K ep:212 epch:52.97 loss:0.187 grdn:4.232 lr:1.0e-05 updt_s:0.125 data_s:0.779
Training:  60%|██████    | 12100/20000 [3:07:16<1:28:25,  1.49step/s]INFO 2026-04-07 22:43:29 ot_train.py:439 step:22K smpl:177K ep:212 epch:53.01 loss:0.185 grdn:4.241 lr:1.0e-05 updt_s:0.123 data_s:0.779
Training:  61%|██████    | 12120/20000 [3:07:35<1:13:52,  1.78step/s]INFO 2026-04-07 22:43:47 ot_train.py:439 step:22K smpl:177K ep:212 epch:53.06 loss:0.179 grdn:3.627 lr:1.0e-05 updt_s:0.125 data_s:0.813
Training:  61%|██████    | 12140/20000 [3:07:53<1:13:12,  1.79step/s]INFO 2026-04-07 22:44:06 ot_train.py:439 step:22K smpl:177K ep:212 epch:53.11 loss:0.190 grdn:4.090 lr:1.0e-05 updt_s:0.125 data_s:0.796
Training:  61%|██████    | 12160/20000 [3:08:12<1:13:20,  1.78step/s]INFO 2026-04-07 22:44:25 ot_train.py:439 step:22K smpl:177K ep:213 epch:53.16 loss:0.186 grdn:3.989 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  61%|██████    | 12180/20000 [3:08:31<1:17:04,  1.69step/s]INFO 2026-04-07 22:44:43 ot_train.py:439 step:22K smpl:177K ep:213 epch:53.21 loss:0.185 grdn:4.258 lr:1.0e-05 updt_s:0.125 data_s:0.802
Training:  61%|██████    | 12200/20000 [3:08:50<1:23:05,  1.56step/s]INFO 2026-04-07 22:45:02 ot_train.py:439 step:22K smpl:178K ep:213 epch:53.25 loss:0.188 grdn:4.188 lr:1.0e-05 updt_s:0.124 data_s:0.835
Training:  61%|██████    | 12220/20000 [3:09:09<1:21:37,  1.59step/s]INFO 2026-04-07 22:45:21 ot_train.py:439 step:22K smpl:178K ep:213 epch:53.30 loss:0.188 grdn:4.358 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  61%|██████    | 12240/20000 [3:09:28<1:29:12,  1.45step/s]INFO 2026-04-07 22:45:41 ot_train.py:439 step:22K smpl:178K ep:213 epch:53.35 loss:0.186 grdn:4.339 lr:1.0e-05 updt_s:0.124 data_s:0.842
Training:  61%|██████▏   | 12260/20000 [3:09:47<1:56:27,  1.11step/s]INFO 2026-04-07 22:46:00 ot_train.py:439 step:22K smpl:178K ep:214 epch:53.40 loss:0.186 grdn:4.703 lr:1.0e-05 updt_s:0.123 data_s:0.849
Training:  61%|██████▏   | 12280/20000 [3:10:06<2:05:14,  1.03step/s]INFO 2026-04-07 22:46:19 ot_train.py:439 step:22K smpl:178K ep:214 epch:53.45 loss:0.191 grdn:4.302 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  62%|██████▏   | 12300/20000 [3:10:25<2:06:55,  1.01step/s]INFO 2026-04-07 22:46:37 ot_train.py:439 step:22K smpl:178K ep:214 epch:53.49 loss:0.192 grdn:4.944 lr:1.0e-05 updt_s:0.125 data_s:0.805
Training:  62%|██████▏   | 12320/20000 [3:10:43<2:03:52,  1.03step/s]INFO 2026-04-07 22:46:56 ot_train.py:439 step:22K smpl:179K ep:214 epch:53.54 loss:0.186 grdn:4.193 lr:1.0e-05 updt_s:0.125 data_s:0.805
Training:  62%|██████▏   | 12340/20000 [3:11:02<2:02:57,  1.04step/s]INFO 2026-04-07 22:47:15 ot_train.py:439 step:22K smpl:179K ep:214 epch:53.59 loss:0.191 grdn:4.237 lr:1.0e-05 updt_s:0.124 data_s:0.817
Training:  62%|██████▏   | 12360/20000 [3:11:21<2:00:29,  1.06step/s]INFO 2026-04-07 22:47:34 ot_train.py:439 step:22K smpl:179K ep:215 epch:53.64 loss:0.188 grdn:4.250 lr:1.0e-05 updt_s:0.123 data_s:0.814
Training:  62%|██████▏   | 12380/20000 [3:11:40<1:57:09,  1.08step/s]INFO 2026-04-07 22:47:52 ot_train.py:439 step:22K smpl:179K ep:215 epch:53.69 loss:0.193 grdn:4.496 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:  62%|██████▏   | 12400/20000 [3:11:58<2:00:09,  1.05step/s]INFO 2026-04-07 22:48:11 ot_train.py:439 step:22K smpl:179K ep:215 epch:53.73 loss:0.183 grdn:4.667 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  62%|██████▏   | 12420/20000 [3:12:17<1:47:16,  1.18step/s]INFO 2026-04-07 22:48:30 ot_train.py:439 step:22K smpl:179K ep:215 epch:53.78 loss:0.190 grdn:4.653 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:  62%|██████▏   | 12440/20000 [3:12:35<1:46:16,  1.19step/s]INFO 2026-04-07 22:48:48 ot_train.py:439 step:22K smpl:180K ep:215 epch:53.83 loss:0.178 grdn:4.267 lr:1.0e-05 updt_s:0.123 data_s:0.798
Training:  62%|██████▏   | 12460/20000 [3:12:54<1:45:37,  1.19step/s]INFO 2026-04-07 22:49:06 ot_train.py:439 step:22K smpl:180K ep:216 epch:53.88 loss:0.187 grdn:4.508 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  62%|██████▏   | 12480/20000 [3:13:12<1:46:14,  1.18step/s]INFO 2026-04-07 22:49:25 ot_train.py:439 step:22K smpl:180K ep:216 epch:53.93 loss:0.192 grdn:4.404 lr:1.0e-05 updt_s:0.124 data_s:0.804
Training:  62%|██████▎   | 12500/20000 [3:13:31<1:52:09,  1.11step/s]INFO 2026-04-07 22:49:44 ot_train.py:439 step:22K smpl:180K ep:216 epch:53.97 loss:0.182 grdn:4.361 lr:1.0e-05 updt_s:0.123 data_s:0.826
Training:  63%|██████▎   | 12520/20000 [3:13:51<1:46:09,  1.17step/s]INFO 2026-04-07 22:50:04 ot_train.py:439 step:23K smpl:180K ep:216 epch:54.02 loss:0.183 grdn:4.054 lr:1.0e-05 updt_s:0.123 data_s:0.868
Training:  63%|██████▎   | 12540/20000 [3:14:10<2:04:08,  1.00step/s]INFO 2026-04-07 22:50:22 ot_train.py:439 step:23K smpl:180K ep:216 epch:54.07 loss:0.186 grdn:4.507 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  63%|██████▎   | 12560/20000 [3:14:28<2:19:30,  1.13s/step]INFO 2026-04-07 22:50:41 ot_train.py:439 step:23K smpl:180K ep:216 epch:54.12 loss:0.187 grdn:4.440 lr:1.0e-05 updt_s:0.123 data_s:0.802
Training:  63%|██████▎   | 12580/20000 [3:14:47<2:46:47,  1.35s/step]INFO 2026-04-07 22:51:00 ot_train.py:439 step:23K smpl:181K ep:217 epch:54.16 loss:0.184 grdn:4.355 lr:1.0e-05 updt_s:0.123 data_s:0.822
Training:  63%|██████▎   | 12600/20000 [3:15:07<3:02:06,  1.48s/step]INFO 2026-04-07 22:51:19 ot_train.py:439 step:23K smpl:181K ep:217 epch:54.21 loss:0.185 grdn:3.952 lr:1.0e-05 updt_s:0.124 data_s:0.847
Training:  63%|██████▎   | 12620/20000 [3:15:25<2:52:41,  1.40s/step]INFO 2026-04-07 22:51:38 ot_train.py:439 step:23K smpl:181K ep:217 epch:54.26 loss:0.180 grdn:4.050 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  63%|██████▎   | 12640/20000 [3:15:44<2:43:58,  1.34s/step]INFO 2026-04-07 22:51:57 ot_train.py:439 step:23K smpl:181K ep:217 epch:54.31 loss:0.193 grdn:4.558 lr:1.0e-05 updt_s:0.132 data_s:0.814
Training:  63%|██████▎   | 12660/20000 [3:16:03<2:41:30,  1.32s/step]INFO 2026-04-07 22:52:16 ot_train.py:439 step:23K smpl:181K ep:217 epch:54.36 loss:0.186 grdn:4.246 lr:1.0e-05 updt_s:0.123 data_s:0.807
Training:  63%|██████▎   | 12680/20000 [3:16:21<2:42:50,  1.33s/step]INFO 2026-04-07 22:52:34 ot_train.py:439 step:23K smpl:181K ep:218 epch:54.40 loss:0.184 grdn:4.575 lr:1.0e-05 updt_s:0.124 data_s:0.792
Training:  64%|██████▎   | 12700/20000 [3:16:39<2:31:29,  1.25s/step]INFO 2026-04-07 22:52:52 ot_train.py:439 step:23K smpl:182K ep:218 epch:54.45 loss:0.191 grdn:4.670 lr:1.0e-05 updt_s:0.124 data_s:0.778
Training:  64%|██████▎   | 12720/20000 [3:16:58<2:10:04,  1.07s/step]INFO 2026-04-07 22:53:11 ot_train.py:439 step:23K smpl:182K ep:218 epch:54.50 loss:0.184 grdn:4.271 lr:1.0e-05 updt_s:0.123 data_s:0.811
Training:  64%|██████▎   | 12740/20000 [3:17:17<2:12:24,  1.09s/step]INFO 2026-04-07 22:53:30 ot_train.py:439 step:23K smpl:182K ep:218 epch:54.55 loss:0.181 grdn:3.984 lr:1.0e-05 updt_s:0.123 data_s:0.817
Training:  64%|██████▍   | 12760/20000 [3:17:36<2:02:47,  1.02s/step]INFO 2026-04-07 22:53:48 ot_train.py:439 step:23K smpl:182K ep:218 epch:54.60 loss:0.184 grdn:4.539 lr:1.0e-05 updt_s:0.123 data_s:0.811
Training:  64%|██████▍   | 12780/20000 [3:17:54<1:53:44,  1.06step/s]INFO 2026-04-07 22:54:07 ot_train.py:439 step:23K smpl:182K ep:219 epch:54.64 loss:0.192 grdn:4.595 lr:1.0e-05 updt_s:0.122 data_s:0.811
Training:  64%|██████▍   | 12800/20000 [3:18:13<1:41:38,  1.18step/s]INFO 2026-04-07 22:54:25 ot_train.py:439 step:23K smpl:182K ep:219 epch:54.69 loss:0.193 grdn:4.313 lr:1.0e-05 updt_s:0.123 data_s:0.797
Training:  64%|██████▍   | 12820/20000 [3:18:31<1:29:41,  1.33step/s]INFO 2026-04-07 22:54:44 ot_train.py:439 step:23K smpl:183K ep:219 epch:54.74 loss:0.184 grdn:4.342 lr:1.0e-05 updt_s:0.123 data_s:0.790
Training:  64%|██████▍   | 12840/20000 [3:18:49<1:26:51,  1.37step/s]INFO 2026-04-07 22:55:02 ot_train.py:439 step:23K smpl:183K ep:219 epch:54.79 loss:0.191 grdn:4.370 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:  64%|██████▍   | 12860/20000 [3:19:08<1:43:05,  1.15step/s]INFO 2026-04-07 22:55:20 ot_train.py:439 step:23K smpl:183K ep:219 epch:54.84 loss:0.181 grdn:4.045 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  64%|██████▍   | 12880/20000 [3:19:26<1:59:32,  1.01s/step]INFO 2026-04-07 22:55:39 ot_train.py:439 step:23K smpl:183K ep:220 epch:54.88 loss:0.191 grdn:4.307 lr:1.0e-05 updt_s:0.123 data_s:0.811
Training:  64%|██████▍   | 12900/20000 [3:19:45<2:02:53,  1.04s/step]INFO 2026-04-07 22:55:57 ot_train.py:439 step:23K smpl:183K ep:220 epch:54.93 loss:0.182 grdn:4.065 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  65%|██████▍   | 12920/20000 [3:20:03<1:48:15,  1.09step/s]INFO 2026-04-07 22:56:16 ot_train.py:439 step:23K smpl:183K ep:220 epch:54.98 loss:0.186 grdn:4.789 lr:1.0e-05 updt_s:0.123 data_s:0.809
Training:  65%|██████▍   | 12940/20000 [3:20:25<2:08:50,  1.09s/step]INFO 2026-04-07 22:56:37 ot_train.py:439 step:23K smpl:184K ep:220 epch:55.03 loss:0.186 grdn:4.121 lr:1.0e-05 updt_s:0.124 data_s:0.936
Training:  65%|██████▍   | 12960/20000 [3:20:43<2:22:04,  1.21s/step]INFO 2026-04-07 22:56:56 ot_train.py:439 step:23K smpl:184K ep:220 epch:55.08 loss:0.182 grdn:4.385 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  65%|██████▍   | 12980/20000 [3:21:01<2:20:55,  1.20s/step]INFO 2026-04-07 22:57:14 ot_train.py:439 step:23K smpl:184K ep:220 epch:55.12 loss:0.172 grdn:3.733 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:  65%|██████▌   | 13000/20000 [3:21:19<2:29:34,  1.28s/step]INFO 2026-04-07 22:57:32 ot_train.py:439 step:23K smpl:184K ep:221 epch:55.17 loss:0.179 grdn:4.311 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  65%|██████▌   | 13020/20000 [3:21:38<2:03:08,  1.06s/step]INFO 2026-04-07 22:57:50 ot_train.py:439 step:23K smpl:184K ep:221 epch:55.22 loss:0.185 grdn:3.926 lr:1.0e-05 updt_s:0.123 data_s:0.779
Training:  65%|██████▌   | 13040/20000 [3:21:56<1:41:39,  1.14step/s]INFO 2026-04-07 22:58:09 ot_train.py:439 step:23K smpl:184K ep:221 epch:55.27 loss:0.184 grdn:4.683 lr:1.0e-05 updt_s:0.123 data_s:0.793
Training:  65%|██████▌   | 13060/20000 [3:22:14<1:36:49,  1.19step/s]INFO 2026-04-07 22:58:27 ot_train.py:439 step:23K smpl:184K ep:221 epch:55.32 loss:0.192 grdn:4.161 lr:1.0e-05 updt_s:0.123 data_s:0.786
Training:  65%|██████▌   | 13080/20000 [3:22:32<1:06:20,  1.74step/s]INFO 2026-04-07 22:58:45 ot_train.py:439 step:23K smpl:185K ep:221 epch:55.36 loss:0.181 grdn:4.385 lr:1.0e-05 updt_s:0.123 data_s:0.771
Training:  66%|██████▌   | 13100/20000 [3:22:51<1:02:20,  1.84step/s]INFO 2026-04-07 22:59:03 ot_train.py:439 step:23K smpl:185K ep:222 epch:55.41 loss:0.186 grdn:4.506 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  66%|██████▌   | 13120/20000 [3:23:09<1:06:43,  1.72step/s]INFO 2026-04-07 22:59:22 ot_train.py:439 step:23K smpl:185K ep:222 epch:55.46 loss:0.186 grdn:3.937 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  66%|██████▌   | 13140/20000 [3:23:28<1:04:46,  1.77step/s]INFO 2026-04-07 22:59:41 ot_train.py:439 step:23K smpl:185K ep:222 epch:55.51 loss:0.178 grdn:3.837 lr:1.0e-05 updt_s:0.124 data_s:0.821
Training:  66%|██████▌   | 13160/20000 [3:23:47<1:02:28,  1.82step/s]INFO 2026-04-07 22:59:59 ot_train.py:439 step:23K smpl:185K ep:222 epch:55.56 loss:0.188 grdn:4.064 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  66%|██████▌   | 13180/20000 [3:24:05<1:00:34,  1.88step/s]INFO 2026-04-07 23:00:17 ot_train.py:439 step:23K smpl:185K ep:222 epch:55.60 loss:0.180 grdn:5.044 lr:1.0e-05 updt_s:0.125 data_s:0.773
Training:  66%|██████▌   | 13200/20000 [3:24:24<1:06:15,  1.71step/s]INFO 2026-04-07 23:00:36 ot_train.py:439 step:23K smpl:186K ep:223 epch:55.65 loss:0.187 grdn:4.699 lr:1.0e-05 updt_s:0.124 data_s:0.825
Training:  66%|██████▌   | 13220/20000 [3:24:42<1:05:03,  1.74step/s]INFO 2026-04-07 23:00:55 ot_train.py:439 step:23K smpl:186K ep:223 epch:55.70 loss:0.182 grdn:4.568 lr:1.0e-05 updt_s:0.123 data_s:0.805
Training:  66%|██████▌   | 13240/20000 [3:25:00<1:01:28,  1.83step/s]INFO 2026-04-07 23:01:13 ot_train.py:439 step:23K smpl:186K ep:223 epch:55.75 loss:0.198 grdn:5.079 lr:1.0e-05 updt_s:0.123 data_s:0.781
Training:  66%|██████▋   | 13260/20000 [3:25:19<1:03:10,  1.78step/s]INFO 2026-04-07 23:01:32 ot_train.py:439 step:23K smpl:186K ep:223 epch:55.80 loss:0.181 grdn:4.199 lr:1.0e-05 updt_s:0.124 data_s:0.821
Training:  66%|██████▋   | 13280/20000 [3:25:38<1:04:24,  1.74step/s]INFO 2026-04-07 23:01:51 ot_train.py:439 step:23K smpl:186K ep:223 epch:55.84 loss:0.189 grdn:4.503 lr:1.0e-05 updt_s:0.124 data_s:0.817
Training:  66%|██████▋   | 13300/20000 [3:25:57<1:03:22,  1.76step/s]INFO 2026-04-07 23:02:09 ot_train.py:439 step:23K smpl:186K ep:224 epch:55.89 loss:0.187 grdn:4.015 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  67%|██████▋   | 13320/20000 [3:26:16<1:02:25,  1.78step/s]INFO 2026-04-07 23:02:28 ot_train.py:439 step:23K smpl:187K ep:224 epch:55.94 loss:0.189 grdn:4.511 lr:1.0e-05 updt_s:0.123 data_s:0.813
Training:  67%|██████▋   | 13340/20000 [3:26:34<1:00:17,  1.84step/s]INFO 2026-04-07 23:02:47 ot_train.py:439 step:23K smpl:187K ep:224 epch:55.99 loss:0.185 grdn:4.218 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  67%|██████▋   | 13360/20000 [3:26:56<2:32:51,  1.38s/step]INFO 2026-04-07 23:03:09 ot_train.py:439 step:23K smpl:187K ep:224 epch:56.04 loss:0.183 grdn:5.050 lr:1.0e-05 updt_s:0.124 data_s:0.996
Training:  67%|██████▋   | 13380/20000 [3:27:15<2:29:29,  1.35s/step]INFO 2026-04-07 23:03:28 ot_train.py:439 step:23K smpl:187K ep:224 epch:56.08 loss:0.181 grdn:4.447 lr:1.0e-05 updt_s:0.125 data_s:0.802
Training:  67%|██████▋   | 13400/20000 [3:27:33<2:09:57,  1.18s/step]INFO 2026-04-07 23:03:46 ot_train.py:439 step:23K smpl:187K ep:225 epch:56.13 loss:0.190 grdn:5.012 lr:1.0e-05 updt_s:0.125 data_s:0.789
Training:  67%|██████▋   | 13420/20000 [3:27:51<1:49:53,  1.00s/step]INFO 2026-04-07 23:04:04 ot_train.py:439 step:23K smpl:187K ep:225 epch:56.18 loss:0.182 grdn:4.006 lr:1.0e-05 updt_s:0.124 data_s:0.783
Training:  67%|██████▋   | 13440/20000 [3:28:10<1:47:38,  1.02step/s]INFO 2026-04-07 23:04:22 ot_train.py:439 step:23K smpl:188K ep:225 epch:56.23 loss:0.190 grdn:4.395 lr:1.0e-05 updt_s:0.124 data_s:0.785
Training:  67%|██████▋   | 13460/20000 [3:28:28<1:35:42,  1.14step/s]INFO 2026-04-07 23:04:41 ot_train.py:439 step:23K smpl:188K ep:225 epch:56.28 loss:0.187 grdn:4.726 lr:1.0e-05 updt_s:0.123 data_s:0.793
Training:  67%|██████▋   | 13480/20000 [3:28:47<1:37:41,  1.11step/s]INFO 2026-04-07 23:04:59 ot_train.py:439 step:23K smpl:188K ep:225 epch:56.32 loss:0.178 grdn:4.061 lr:1.0e-05 updt_s:0.122 data_s:0.815
Training:  68%|██████▊   | 13500/20000 [3:29:05<1:09:33,  1.56step/s]INFO 2026-04-07 23:05:17 ot_train.py:439 step:24K smpl:188K ep:225 epch:56.37 loss:0.184 grdn:4.447 lr:1.0e-05 updt_s:0.124 data_s:0.783
Training:  68%|██████▊   | 13520/20000 [3:29:23<1:04:08,  1.68step/s]INFO 2026-04-07 23:05:36 ot_train.py:439 step:24K smpl:188K ep:226 epch:56.42 loss:0.183 grdn:4.198 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:  68%|██████▊   | 13540/20000 [3:29:42<1:01:48,  1.74step/s]INFO 2026-04-07 23:05:54 ot_train.py:439 step:24K smpl:188K ep:226 epch:56.47 loss:0.184 grdn:4.006 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  68%|██████▊   | 13560/20000 [3:30:00<59:53,  1.79step/s]  INFO 2026-04-07 23:06:13 ot_train.py:439 step:24K smpl:188K ep:226 epch:56.52 loss:0.178 grdn:4.048 lr:1.0e-05 updt_s:0.125 data_s:0.808
Training:  68%|██████▊   | 13580/20000 [3:30:19<1:02:38,  1.71step/s]INFO 2026-04-07 23:06:32 ot_train.py:439 step:24K smpl:189K ep:226 epch:56.56 loss:0.181 grdn:3.692 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  68%|██████▊   | 13600/20000 [3:30:38<1:00:08,  1.77step/s]INFO 2026-04-07 23:06:51 ot_train.py:439 step:24K smpl:189K ep:226 epch:56.61 loss:0.181 grdn:4.505 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  68%|██████▊   | 13620/20000 [3:30:57<1:00:59,  1.74step/s]INFO 2026-04-07 23:07:10 ot_train.py:439 step:24K smpl:189K ep:227 epch:56.66 loss:0.178 grdn:4.699 lr:1.0e-05 updt_s:0.123 data_s:0.831
Training:  68%|██████▊   | 13640/20000 [3:31:16<58:14,  1.82step/s]  INFO 2026-04-07 23:07:29 ot_train.py:439 step:24K smpl:189K ep:227 epch:56.71 loss:0.184 grdn:4.343 lr:1.0e-05 updt_s:0.125 data_s:0.822
Training:  68%|██████▊   | 13660/20000 [3:31:36<1:02:14,  1.70step/s]INFO 2026-04-07 23:07:48 ot_train.py:439 step:24K smpl:189K ep:227 epch:56.76 loss:0.188 grdn:5.209 lr:1.0e-05 updt_s:0.124 data_s:0.839
Training:  68%|██████▊   | 13680/20000 [3:31:55<1:01:45,  1.71step/s]INFO 2026-04-07 23:08:08 ot_train.py:439 step:24K smpl:189K ep:227 epch:56.80 loss:0.183 grdn:4.586 lr:1.0e-05 updt_s:0.124 data_s:0.851
Training:  68%|██████▊   | 13700/20000 [3:32:14<1:00:07,  1.75step/s]INFO 2026-04-07 23:08:27 ot_train.py:439 step:24K smpl:190K ep:227 epch:56.85 loss:0.183 grdn:4.591 lr:1.0e-05 updt_s:0.126 data_s:0.818
Training:  69%|██████▊   | 13720/20000 [3:32:33<1:00:06,  1.74step/s]INFO 2026-04-07 23:08:45 ot_train.py:439 step:24K smpl:190K ep:228 epch:56.90 loss:0.189 grdn:4.813 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  69%|██████▊   | 13740/20000 [3:32:52<1:00:28,  1.73step/s]INFO 2026-04-07 23:09:04 ot_train.py:439 step:24K smpl:190K ep:228 epch:56.95 loss:0.179 grdn:4.139 lr:1.0e-05 updt_s:0.125 data_s:0.830
Training:  69%|██████▉   | 13760/20000 [3:33:10<51:36,  2.02step/s]  INFO 2026-04-07 23:09:22 ot_train.py:439 step:24K smpl:190K ep:228 epch:57.00 loss:0.188 grdn:4.350 lr:1.0e-05 updt_s:0.124 data_s:0.769
Training:  69%|██████▉   | 13780/20000 [3:33:30<58:54,  1.76step/s]  INFO 2026-04-07 23:09:42 ot_train.py:439 step:24K smpl:190K ep:228 epch:57.04 loss:0.182 grdn:4.564 lr:1.0e-05 updt_s:0.125 data_s:0.879
Training:  69%|██████▉   | 13800/20000 [3:33:49<1:00:01,  1.72step/s]INFO 2026-04-07 23:10:01 ot_train.py:439 step:24K smpl:190K ep:228 epch:57.09 loss:0.183 grdn:4.910 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  69%|██████▉   | 13820/20000 [3:34:08<1:01:35,  1.67step/s]INFO 2026-04-07 23:10:20 ot_train.py:439 step:24K smpl:191K ep:229 epch:57.14 loss:0.187 grdn:4.311 lr:1.0e-05 updt_s:0.133 data_s:0.822
Training:  69%|██████▉   | 13840/20000 [3:34:27<59:24,  1.73step/s]  INFO 2026-04-07 23:10:39 ot_train.py:439 step:24K smpl:191K ep:229 epch:57.19 loss:0.183 grdn:4.094 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  69%|██████▉   | 13860/20000 [3:34:45<56:13,  1.82step/s]  INFO 2026-04-07 23:10:58 ot_train.py:439 step:24K smpl:191K ep:229 epch:57.24 loss:0.182 grdn:4.230 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  69%|██████▉   | 13880/20000 [3:35:04<55:12,  1.85step/s]  INFO 2026-04-07 23:11:16 ot_train.py:439 step:24K smpl:191K ep:229 epch:57.28 loss:0.181 grdn:4.519 lr:1.0e-05 updt_s:0.125 data_s:0.803
Training:  70%|██████▉   | 13900/20000 [3:35:22<55:24,  1.83step/s]  INFO 2026-04-07 23:11:34 ot_train.py:439 step:24K smpl:191K ep:229 epch:57.33 loss:0.183 grdn:4.439 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  70%|██████▉   | 13920/20000 [3:35:40<1:03:35,  1.59step/s]INFO 2026-04-07 23:11:53 ot_train.py:439 step:24K smpl:191K ep:230 epch:57.38 loss:0.181 grdn:4.968 lr:1.0e-05 updt_s:0.125 data_s:0.779
Training:  70%|██████▉   | 13940/20000 [3:35:59<1:25:53,  1.18step/s]INFO 2026-04-07 23:12:11 ot_train.py:439 step:24K smpl:192K ep:230 epch:57.43 loss:0.184 grdn:4.007 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  70%|██████▉   | 13960/20000 [3:36:18<1:38:48,  1.02step/s]INFO 2026-04-07 23:12:30 ot_train.py:439 step:24K smpl:192K ep:230 epch:57.48 loss:0.181 grdn:4.742 lr:1.0e-05 updt_s:0.123 data_s:0.823
Training:  70%|██████▉   | 13980/20000 [3:36:36<1:41:49,  1.01s/step]INFO 2026-04-07 23:12:49 ot_train.py:439 step:24K smpl:192K ep:230 epch:57.52 loss:0.181 grdn:4.601 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  70%|███████   | 14000/20000 [3:36:55<1:50:29,  1.10s/step]INFO 2026-04-07 23:13:08 ot_train.py:439 step:24K smpl:192K ep:230 epch:57.57 loss:0.183 grdn:4.395 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  70%|███████   | 14020/20000 [3:37:14<2:02:35,  1.23s/step]INFO 2026-04-07 23:13:26 ot_train.py:439 step:24K smpl:192K ep:230 epch:57.62 loss:0.182 grdn:4.168 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  70%|███████   | 14040/20000 [3:37:32<2:19:57,  1.41s/step]INFO 2026-04-07 23:13:45 ot_train.py:439 step:24K smpl:192K ep:231 epch:57.67 loss:0.179 grdn:4.354 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  70%|███████   | 14060/20000 [3:37:51<2:20:49,  1.42s/step]INFO 2026-04-07 23:14:04 ot_train.py:439 step:24K smpl:192K ep:231 epch:57.72 loss:0.190 grdn:4.237 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  70%|███████   | 14080/20000 [3:38:09<2:14:29,  1.36s/step]INFO 2026-04-07 23:14:22 ot_train.py:439 step:24K smpl:193K ep:231 epch:57.76 loss:0.179 grdn:3.962 lr:1.0e-05 updt_s:0.123 data_s:0.785
Training:  70%|███████   | 14100/20000 [3:38:28<2:09:27,  1.32s/step]INFO 2026-04-07 23:14:40 ot_train.py:439 step:24K smpl:193K ep:231 epch:57.81 loss:0.189 grdn:4.738 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  71%|███████   | 14120/20000 [3:38:46<2:12:03,  1.35s/step]INFO 2026-04-07 23:14:59 ot_train.py:439 step:24K smpl:193K ep:231 epch:57.86 loss:0.180 grdn:4.373 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:  71%|███████   | 14140/20000 [3:39:04<1:57:46,  1.21s/step]INFO 2026-04-07 23:15:17 ot_train.py:439 step:24K smpl:193K ep:232 epch:57.91 loss:0.181 grdn:4.111 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  71%|███████   | 14160/20000 [3:39:23<1:43:39,  1.07s/step]INFO 2026-04-07 23:15:35 ot_train.py:439 step:24K smpl:193K ep:232 epch:57.96 loss:0.183 grdn:4.101 lr:1.0e-05 updt_s:0.123 data_s:0.790
Training:  71%|███████   | 14180/20000 [3:39:42<2:03:16,  1.27s/step]INFO 2026-04-07 23:15:55 ot_train.py:439 step:24K smpl:193K ep:232 epch:58.00 loss:0.171 grdn:4.010 lr:1.0e-05 updt_s:0.121 data_s:0.851
Training:  71%|███████   | 14200/20000 [3:40:01<1:15:22,  1.28step/s]INFO 2026-04-07 23:16:14 ot_train.py:439 step:24K smpl:194K ep:232 epch:58.05 loss:0.181 grdn:5.159 lr:1.0e-05 updt_s:0.125 data_s:0.836
Training:  71%|███████   | 14220/20000 [3:40:21<1:16:22,  1.26step/s]INFO 2026-04-07 23:16:33 ot_train.py:439 step:24K smpl:194K ep:232 epch:58.10 loss:0.179 grdn:4.662 lr:1.0e-05 updt_s:0.124 data_s:0.842
Training:  71%|███████   | 14240/20000 [3:40:39<1:10:42,  1.36step/s]INFO 2026-04-07 23:16:52 ot_train.py:439 step:24K smpl:194K ep:233 epch:58.15 loss:0.178 grdn:4.474 lr:1.0e-05 updt_s:0.123 data_s:0.803
Training:  71%|███████▏  | 14260/20000 [3:40:58<1:11:01,  1.35step/s]INFO 2026-04-07 23:17:11 ot_train.py:439 step:24K smpl:194K ep:233 epch:58.19 loss:0.179 grdn:4.140 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  71%|███████▏  | 14280/20000 [3:41:16<1:10:27,  1.35step/s]INFO 2026-04-07 23:17:29 ot_train.py:439 step:24K smpl:194K ep:233 epch:58.24 loss:0.186 grdn:4.193 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  72%|███████▏  | 14300/20000 [3:41:36<1:14:26,  1.28step/s]INFO 2026-04-07 23:17:48 ot_train.py:439 step:24K smpl:194K ep:233 epch:58.29 loss:0.179 grdn:4.055 lr:1.0e-05 updt_s:0.125 data_s:0.837
Training:  72%|███████▏  | 14320/20000 [3:41:55<1:13:37,  1.29step/s]INFO 2026-04-07 23:18:07 ot_train.py:439 step:24K smpl:195K ep:233 epch:58.34 loss:0.178 grdn:4.371 lr:1.0e-05 updt_s:0.125 data_s:0.825
Training:  72%|███████▏  | 14340/20000 [3:42:14<1:12:35,  1.30step/s]INFO 2026-04-07 23:18:26 ot_train.py:439 step:24K smpl:195K ep:234 epch:58.39 loss:0.185 grdn:4.088 lr:1.0e-05 updt_s:0.125 data_s:0.824
Training:  72%|███████▏  | 14360/20000 [3:42:32<1:09:57,  1.34step/s]INFO 2026-04-07 23:18:45 ot_train.py:439 step:24K smpl:195K ep:234 epch:58.43 loss:0.187 grdn:4.873 lr:1.0e-05 updt_s:0.125 data_s:0.792
Training:  72%|███████▏  | 14380/20000 [3:42:50<1:08:56,  1.36step/s]INFO 2026-04-07 23:19:03 ot_train.py:439 step:24K smpl:195K ep:234 epch:58.48 loss:0.176 grdn:3.691 lr:1.0e-05 updt_s:0.125 data_s:0.786
Training:  72%|███████▏  | 14400/20000 [3:43:08<1:06:25,  1.40step/s]INFO 2026-04-07 23:19:21 ot_train.py:439 step:24K smpl:195K ep:234 epch:58.53 loss:0.180 grdn:4.041 lr:1.0e-05 updt_s:0.124 data_s:0.768
Training:  72%|███████▏  | 14420/20000 [3:43:26<1:08:51,  1.35step/s]INFO 2026-04-07 23:19:39 ot_train.py:439 step:24K smpl:195K ep:234 epch:58.58 loss:0.180 grdn:3.949 lr:1.0e-05 updt_s:0.124 data_s:0.792
Training:  72%|███████▏  | 14440/20000 [3:43:45<1:10:22,  1.32step/s]INFO 2026-04-07 23:19:58 ot_train.py:439 step:24K smpl:196K ep:235 epch:58.63 loss:0.185 grdn:4.703 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  72%|███████▏  | 14460/20000 [3:44:04<1:07:07,  1.38step/s]INFO 2026-04-07 23:20:16 ot_train.py:439 step:24K smpl:196K ep:235 epch:58.67 loss:0.185 grdn:4.200 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  72%|███████▏  | 14480/20000 [3:44:23<1:16:08,  1.21step/s]INFO 2026-04-07 23:20:35 ot_train.py:439 step:24K smpl:196K ep:235 epch:58.72 loss:0.182 grdn:3.878 lr:1.0e-05 updt_s:0.124 data_s:0.824
Training:  72%|███████▎  | 14500/20000 [3:44:41<1:13:29,  1.25step/s]INFO 2026-04-07 23:20:54 ot_train.py:439 step:24K smpl:196K ep:235 epch:58.77 loss:0.180 grdn:4.192 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  73%|███████▎  | 14520/20000 [3:45:00<1:10:38,  1.29step/s]INFO 2026-04-07 23:21:12 ot_train.py:439 step:25K smpl:196K ep:235 epch:58.82 loss:0.175 grdn:4.395 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  73%|███████▎  | 14540/20000 [3:45:18<1:08:40,  1.33step/s]INFO 2026-04-07 23:21:31 ot_train.py:439 step:25K smpl:196K ep:235 epch:58.87 loss:0.182 grdn:4.126 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  73%|███████▎  | 14560/20000 [3:45:37<1:08:38,  1.32step/s]INFO 2026-04-07 23:21:49 ot_train.py:439 step:25K smpl:196K ep:236 epch:58.91 loss:0.183 grdn:4.082 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  73%|███████▎  | 14580/20000 [3:45:56<1:11:07,  1.27step/s]INFO 2026-04-07 23:22:08 ot_train.py:439 step:25K smpl:197K ep:236 epch:58.96 loss:0.184 grdn:3.828 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  73%|███████▎  | 14600/20000 [3:46:17<1:45:26,  1.17s/step]INFO 2026-04-07 23:22:30 ot_train.py:439 step:25K smpl:197K ep:236 epch:59.01 loss:0.178 grdn:3.745 lr:1.0e-05 updt_s:0.123 data_s:0.950
Training:  73%|███████▎  | 14620/20000 [3:46:36<1:36:12,  1.07s/step]INFO 2026-04-07 23:22:49 ot_train.py:439 step:25K smpl:197K ep:236 epch:59.06 loss:0.177 grdn:4.279 lr:1.0e-05 updt_s:0.125 data_s:0.823
Training:  73%|███████▎  | 14640/20000 [3:46:55<1:35:16,  1.07s/step]INFO 2026-04-07 23:23:08 ot_train.py:439 step:25K smpl:197K ep:236 epch:59.11 loss:0.170 grdn:3.804 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  73%|███████▎  | 14660/20000 [3:47:13<1:24:28,  1.05step/s]INFO 2026-04-07 23:23:26 ot_train.py:439 step:25K smpl:197K ep:237 epch:59.15 loss:0.178 grdn:4.541 lr:1.0e-05 updt_s:0.124 data_s:0.780
Training:  73%|███████▎  | 14680/20000 [3:47:32<1:27:12,  1.02step/s]INFO 2026-04-07 23:23:44 ot_train.py:439 step:25K smpl:197K ep:237 epch:59.20 loss:0.187 grdn:4.565 lr:1.0e-05 updt_s:0.123 data_s:0.804
Training:  74%|███████▎  | 14700/20000 [3:47:51<1:32:33,  1.05s/step]INFO 2026-04-07 23:24:03 ot_train.py:439 step:25K smpl:198K ep:237 epch:59.25 loss:0.186 grdn:4.479 lr:1.0e-05 updt_s:0.123 data_s:0.826
Training:  74%|███████▎  | 14720/20000 [3:48:09<1:28:58,  1.01s/step]INFO 2026-04-07 23:24:22 ot_train.py:439 step:25K smpl:198K ep:237 epch:59.30 loss:0.179 grdn:4.132 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  74%|███████▎  | 14740/20000 [3:48:28<1:30:06,  1.03s/step]INFO 2026-04-07 23:24:41 ot_train.py:439 step:25K smpl:198K ep:237 epch:59.35 loss:0.180 grdn:3.885 lr:1.0e-05 updt_s:0.124 data_s:0.824
Training:  74%|███████▍  | 14760/20000 [3:48:47<1:47:19,  1.23s/step]INFO 2026-04-07 23:25:00 ot_train.py:439 step:25K smpl:198K ep:238 epch:59.39 loss:0.180 grdn:4.204 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  74%|███████▍  | 14780/20000 [3:49:06<1:58:24,  1.36s/step]INFO 2026-04-07 23:25:19 ot_train.py:439 step:25K smpl:198K ep:238 epch:59.44 loss:0.183 grdn:3.922 lr:1.0e-05 updt_s:0.124 data_s:0.836
Training:  74%|███████▍  | 14800/20000 [3:49:25<1:55:35,  1.33s/step]INFO 2026-04-07 23:25:38 ot_train.py:439 step:25K smpl:198K ep:238 epch:59.49 loss:0.184 grdn:4.678 lr:1.0e-05 updt_s:0.124 data_s:0.808
Training:  74%|███████▍  | 14820/20000 [3:49:44<1:59:41,  1.39s/step]INFO 2026-04-07 23:25:57 ot_train.py:439 step:25K smpl:199K ep:238 epch:59.54 loss:0.181 grdn:4.525 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  74%|███████▍  | 14840/20000 [3:50:03<2:00:49,  1.40s/step]INFO 2026-04-07 23:26:16 ot_train.py:439 step:25K smpl:199K ep:238 epch:59.59 loss:0.183 grdn:4.033 lr:1.0e-05 updt_s:0.124 data_s:0.844
Training:  74%|███████▍  | 14860/20000 [3:50:23<1:59:19,  1.39s/step]INFO 2026-04-07 23:26:35 ot_train.py:439 step:25K smpl:199K ep:239 epch:59.63 loss:0.180 grdn:4.159 lr:1.0e-05 updt_s:0.125 data_s:0.840
Training:  74%|███████▍  | 14880/20000 [3:50:41<1:47:16,  1.26s/step]INFO 2026-04-07 23:26:53 ot_train.py:439 step:25K smpl:199K ep:239 epch:59.68 loss:0.179 grdn:4.277 lr:1.0e-05 updt_s:0.124 data_s:0.779
Training:  74%|███████▍  | 14900/20000 [3:51:00<1:54:48,  1.35s/step]INFO 2026-04-07 23:27:12 ot_train.py:439 step:25K smpl:199K ep:239 epch:59.73 loss:0.180 grdn:4.777 lr:1.0e-05 updt_s:0.124 data_s:0.827
Training:  75%|███████▍  | 14920/20000 [3:51:19<1:58:57,  1.40s/step]INFO 2026-04-07 23:27:31 ot_train.py:439 step:25K smpl:199K ep:239 epch:59.78 loss:0.179 grdn:4.738 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  75%|███████▍  | 14940/20000 [3:51:39<2:05:49,  1.49s/step]INFO 2026-04-07 23:27:51 ot_train.py:439 step:25K smpl:200K ep:239 epch:59.83 loss:0.183 grdn:4.052 lr:1.0e-05 updt_s:0.124 data_s:0.860
Training:  75%|███████▍  | 14960/20000 [3:51:58<2:01:07,  1.44s/step]INFO 2026-04-07 23:28:10 ot_train.py:439 step:25K smpl:200K ep:239 epch:59.87 loss:0.176 grdn:3.990 lr:1.0e-05 updt_s:0.126 data_s:0.829
Training:  75%|███████▍  | 14980/20000 [3:52:17<2:03:57,  1.48s/step]INFO 2026-04-07 23:28:29 ot_train.py:439 step:25K smpl:200K ep:240 epch:59.92 loss:0.178 grdn:4.018 lr:1.0e-05 updt_s:0.125 data_s:0.829
Training:  75%|███████▌  | 15000/20000 [3:52:35<1:59:32,  1.43s/step]INFO 2026-04-07 23:28:48 ot_train.py:439 step:25K smpl:200K ep:240 epch:59.97 loss:0.180 grdn:4.364 lr:1.0e-05 updt_s:0.125 data_s:0.801
Training:  75%|███████▌  | 15020/20000 [3:52:54<1:52:58,  1.36s/step]INFO 2026-04-07 23:29:07 ot_train.py:439 step:25K smpl:200K ep:240 epch:60.02 loss:0.180 grdn:4.371 lr:1.0e-05 updt_s:0.134 data_s:0.821
Training:  75%|███████▌  | 15040/20000 [3:53:12<1:17:05,  1.07step/s]INFO 2026-04-07 23:29:24 ot_train.py:439 step:25K smpl:200K ep:240 epch:60.07 loss:0.176 grdn:4.182 lr:1.0e-05 updt_s:0.123 data_s:0.738
Training:  75%|███████▌  | 15060/20000 [3:53:29<49:31,  1.66step/s]  INFO 2026-04-07 23:29:42 ot_train.py:439 step:25K smpl:200K ep:240 epch:60.11 loss:0.187 grdn:4.348 lr:1.0e-05 updt_s:0.123 data_s:0.747
Training:  75%|███████▌  | 15080/20000 [3:53:48<48:30,  1.69step/s]  INFO 2026-04-07 23:30:00 ot_train.py:439 step:25K smpl:201K ep:241 epch:60.16 loss:0.174 grdn:3.851 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  76%|███████▌  | 15100/20000 [3:54:06<48:52,  1.67step/s]  INFO 2026-04-07 23:30:19 ot_train.py:439 step:25K smpl:201K ep:241 epch:60.21 loss:0.180 grdn:3.866 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  76%|███████▌  | 15120/20000 [3:54:25<47:49,  1.70step/s]  INFO 2026-04-07 23:30:38 ot_train.py:439 step:25K smpl:201K ep:241 epch:60.26 loss:0.178 grdn:4.598 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  76%|███████▌  | 15140/20000 [3:54:44<49:56,  1.62step/s]  INFO 2026-04-07 23:30:56 ot_train.py:439 step:25K smpl:201K ep:241 epch:60.31 loss:0.173 grdn:3.713 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  76%|███████▌  | 15160/20000 [3:55:02<52:55,  1.52step/s]  INFO 2026-04-07 23:31:15 ot_train.py:439 step:25K smpl:201K ep:241 epch:60.35 loss:0.179 grdn:4.074 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  76%|███████▌  | 15180/20000 [3:55:21<56:39,  1.42step/s]  INFO 2026-04-07 23:31:33 ot_train.py:439 step:25K smpl:201K ep:242 epch:60.40 loss:0.176 grdn:4.151 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  76%|███████▌  | 15200/20000 [3:55:40<1:01:24,  1.30step/s]INFO 2026-04-07 23:31:53 ot_train.py:439 step:25K smpl:202K ep:242 epch:60.45 loss:0.186 grdn:5.000 lr:1.0e-05 updt_s:0.123 data_s:0.833
Training:  76%|███████▌  | 15220/20000 [3:55:58<58:49,  1.35step/s]  INFO 2026-04-07 23:32:11 ot_train.py:439 step:25K smpl:202K ep:242 epch:60.50 loss:0.183 grdn:4.698 lr:1.0e-05 updt_s:0.125 data_s:0.790
Training:  76%|███████▌  | 15240/20000 [3:56:16<54:33,  1.45step/s]  INFO 2026-04-07 23:32:29 ot_train.py:439 step:25K smpl:202K ep:242 epch:60.55 loss:0.176 grdn:4.194 lr:1.0e-05 updt_s:0.124 data_s:0.775
Training:  76%|███████▋  | 15260/20000 [3:56:35<55:33,  1.42step/s]  INFO 2026-04-07 23:32:47 ot_train.py:439 step:25K smpl:202K ep:242 epch:60.59 loss:0.179 grdn:4.396 lr:1.0e-05 updt_s:0.123 data_s:0.807
Training:  76%|███████▋  | 15280/20000 [3:56:54<59:21,  1.33step/s]  INFO 2026-04-07 23:33:06 ot_train.py:439 step:25K smpl:202K ep:243 epch:60.64 loss:0.175 grdn:3.625 lr:1.0e-05 updt_s:0.123 data_s:0.819
Training:  76%|███████▋  | 15300/20000 [3:57:13<59:54,  1.31step/s]  INFO 2026-04-07 23:33:25 ot_train.py:439 step:25K smpl:202K ep:243 epch:60.69 loss:0.174 grdn:4.113 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  77%|███████▋  | 15320/20000 [3:57:31<57:43,  1.35step/s]  INFO 2026-04-07 23:33:43 ot_train.py:439 step:25K smpl:203K ep:243 epch:60.74 loss:0.176 grdn:3.829 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  77%|███████▋  | 15340/20000 [3:57:49<58:29,  1.33step/s]  INFO 2026-04-07 23:34:02 ot_train.py:439 step:25K smpl:203K ep:243 epch:60.79 loss:0.176 grdn:4.429 lr:1.0e-05 updt_s:0.124 data_s:0.785
Training:  77%|███████▋  | 15360/20000 [3:58:08<59:07,  1.31step/s]  INFO 2026-04-07 23:34:21 ot_train.py:439 step:25K smpl:203K ep:243 epch:60.83 loss:0.172 grdn:4.205 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  77%|███████▋  | 15380/20000 [3:58:26<55:17,  1.39step/s]  INFO 2026-04-07 23:34:39 ot_train.py:439 step:25K smpl:203K ep:244 epch:60.88 loss:0.178 grdn:4.270 lr:1.0e-05 updt_s:0.125 data_s:0.792
Training:  77%|███████▋  | 15400/20000 [3:58:45<57:41,  1.33step/s]  INFO 2026-04-07 23:34:58 ot_train.py:439 step:25K smpl:203K ep:244 epch:60.93 loss:0.185 grdn:4.203 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  77%|███████▋  | 15420/20000 [3:59:04<58:22,  1.31step/s]  INFO 2026-04-07 23:35:17 ot_train.py:439 step:25K smpl:203K ep:244 epch:60.98 loss:0.185 grdn:4.186 lr:1.0e-05 updt_s:0.123 data_s:0.841
Training:  77%|███████▋  | 15440/20000 [3:59:24<45:49,  1.66step/s]  INFO 2026-04-07 23:35:36 ot_train.py:439 step:25K smpl:204K ep:244 epch:61.03 loss:0.175 grdn:3.990 lr:1.0e-05 updt_s:0.123 data_s:0.846
Training:  77%|███████▋  | 15460/20000 [3:59:42<40:57,  1.85step/s]INFO 2026-04-07 23:35:55 ot_train.py:439 step:25K smpl:204K ep:244 epch:61.07 loss:0.177 grdn:4.333 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  77%|███████▋  | 15480/20000 [4:00:01<42:01,  1.79step/s]INFO 2026-04-07 23:36:14 ot_train.py:439 step:25K smpl:204K ep:244 epch:61.12 loss:0.177 grdn:3.861 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  78%|███████▊  | 15500/20000 [4:00:20<42:40,  1.76step/s]INFO 2026-04-07 23:36:32 ot_train.py:439 step:26K smpl:204K ep:245 epch:61.17 loss:0.178 grdn:4.043 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  78%|███████▊  | 15520/20000 [4:00:39<42:09,  1.77step/s]INFO 2026-04-07 23:36:51 ot_train.py:439 step:26K smpl:204K ep:245 epch:61.22 loss:0.175 grdn:4.049 lr:1.0e-05 updt_s:0.123 data_s:0.816
Training:  78%|███████▊  | 15540/20000 [4:00:57<44:04,  1.69step/s]INFO 2026-04-07 23:37:10 ot_train.py:439 step:26K smpl:204K ep:245 epch:61.27 loss:0.180 grdn:4.005 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  78%|███████▊  | 15560/20000 [4:01:16<43:47,  1.69step/s]INFO 2026-04-07 23:37:29 ot_train.py:439 step:26K smpl:204K ep:245 epch:61.31 loss:0.186 grdn:4.340 lr:1.0e-05 updt_s:0.123 data_s:0.823
Training:  78%|███████▊  | 15580/20000 [4:01:35<44:37,  1.65step/s]INFO 2026-04-07 23:37:48 ot_train.py:439 step:26K smpl:205K ep:245 epch:61.36 loss:0.175 grdn:4.189 lr:1.0e-05 updt_s:0.124 data_s:0.818
Training:  78%|███████▊  | 15600/20000 [4:01:54<46:04,  1.59step/s]  INFO 2026-04-07 23:38:07 ot_train.py:439 step:26K smpl:205K ep:246 epch:61.41 loss:0.174 grdn:3.920 lr:1.0e-05 updt_s:0.123 data_s:0.838
Training:  78%|███████▊  | 15620/20000 [4:02:13<46:47,  1.56step/s]  INFO 2026-04-07 23:38:26 ot_train.py:439 step:26K smpl:205K ep:246 epch:61.46 loss:0.180 grdn:3.872 lr:1.0e-05 updt_s:0.123 data_s:0.812
Training:  78%|███████▊  | 15640/20000 [4:02:31<47:19,  1.54step/s]  INFO 2026-04-07 23:38:44 ot_train.py:439 step:26K smpl:205K ep:246 epch:61.51 loss:0.184 grdn:4.300 lr:1.0e-05 updt_s:0.123 data_s:0.795
Training:  78%|███████▊  | 15660/20000 [4:02:50<49:52,  1.45step/s]  INFO 2026-04-07 23:39:03 ot_train.py:439 step:26K smpl:205K ep:246 epch:61.55 loss:0.175 grdn:4.637 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  78%|███████▊  | 15680/20000 [4:03:09<51:33,  1.40step/s]  INFO 2026-04-07 23:39:22 ot_train.py:439 step:26K smpl:205K ep:246 epch:61.60 loss:0.180 grdn:4.614 lr:1.0e-05 updt_s:0.123 data_s:0.832
Training:  78%|███████▊  | 15700/20000 [4:03:28<52:26,  1.37step/s]  INFO 2026-04-07 23:39:40 ot_train.py:439 step:26K smpl:206K ep:247 epch:61.65 loss:0.179 grdn:4.156 lr:1.0e-05 updt_s:0.123 data_s:0.804
Training:  79%|███████▊  | 15720/20000 [4:03:46<52:32,  1.36step/s]  INFO 2026-04-07 23:39:59 ot_train.py:439 step:26K smpl:206K ep:247 epch:61.70 loss:0.174 grdn:4.388 lr:1.0e-05 updt_s:0.124 data_s:0.813
Training:  79%|███████▊  | 15740/20000 [4:04:05<53:51,  1.32step/s]  INFO 2026-04-07 23:40:17 ot_train.py:439 step:26K smpl:206K ep:247 epch:61.75 loss:0.175 grdn:3.968 lr:1.0e-05 updt_s:0.125 data_s:0.784
Training:  79%|███████▉  | 15760/20000 [4:04:24<54:33,  1.30step/s]  INFO 2026-04-07 23:40:36 ot_train.py:439 step:26K smpl:206K ep:247 epch:61.79 loss:0.169 grdn:3.949 lr:1.0e-05 updt_s:0.124 data_s:0.831
Training:  79%|███████▉  | 15780/20000 [4:04:43<53:49,  1.31step/s]  INFO 2026-04-07 23:40:55 ot_train.py:439 step:26K smpl:206K ep:247 epch:61.84 loss:0.174 grdn:4.305 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  79%|███████▉  | 15800/20000 [4:05:01<53:12,  1.32step/s]  INFO 2026-04-07 23:41:14 ot_train.py:439 step:26K smpl:206K ep:248 epch:61.89 loss:0.176 grdn:4.649 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  79%|███████▉  | 15820/20000 [4:05:20<53:48,  1.29step/s]  INFO 2026-04-07 23:41:33 ot_train.py:439 step:26K smpl:207K ep:248 epch:61.94 loss:0.180 grdn:4.266 lr:1.0e-05 updt_s:0.124 data_s:0.821
Training:  79%|███████▉  | 15840/20000 [4:05:39<52:10,  1.33step/s]  INFO 2026-04-07 23:41:51 ot_train.py:439 step:26K smpl:207K ep:248 epch:61.99 loss:0.177 grdn:3.919 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  79%|███████▉  | 15860/20000 [4:05:58<55:58,  1.23step/s]  INFO 2026-04-07 23:42:11 ot_train.py:439 step:26K smpl:207K ep:248 epch:62.03 loss:0.175 grdn:3.876 lr:1.0e-05 updt_s:0.123 data_s:0.840
Training:  79%|███████▉  | 15880/20000 [4:06:17<55:37,  1.23step/s]  INFO 2026-04-07 23:42:30 ot_train.py:439 step:26K smpl:207K ep:248 epch:62.08 loss:0.174 grdn:4.313 lr:1.0e-05 updt_s:0.124 data_s:0.846
Training:  80%|███████▉  | 15900/20000 [4:06:36<58:52,  1.16step/s]  INFO 2026-04-07 23:42:49 ot_train.py:439 step:26K smpl:207K ep:249 epch:62.13 loss:0.178 grdn:4.307 lr:1.0e-05 updt_s:0.124 data_s:0.826
Training:  80%|███████▉  | 15920/20000 [4:06:55<58:14,  1.17step/s]  INFO 2026-04-07 23:43:07 ot_train.py:439 step:26K smpl:207K ep:249 epch:62.18 loss:0.174 grdn:4.154 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:  80%|███████▉  | 15940/20000 [4:07:13<59:11,  1.14step/s]  INFO 2026-04-07 23:43:26 ot_train.py:439 step:26K smpl:208K ep:249 epch:62.22 loss:0.174 grdn:4.264 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  80%|███████▉  | 15960/20000 [4:07:32<55:16,  1.22step/s]  INFO 2026-04-07 23:43:44 ot_train.py:439 step:26K smpl:208K ep:249 epch:62.27 loss:0.180 grdn:4.085 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  80%|███████▉  | 15980/20000 [4:07:51<54:17,  1.23step/s]  INFO 2026-04-07 23:44:03 ot_train.py:439 step:26K smpl:208K ep:249 epch:62.32 loss:0.180 grdn:4.520 lr:1.0e-05 updt_s:0.123 data_s:0.817
Training:  80%|████████  | 16000/20000 [4:08:09<48:01,  1.39step/s]  INFO 2026-04-07 23:44:22 ot_train.py:439 step:26K smpl:208K ep:249 epch:62.37 loss:0.180 grdn:4.942 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  80%|████████  | 16020/20000 [4:08:27<47:33,  1.40step/s]  INFO 2026-04-07 23:44:40 ot_train.py:439 step:26K smpl:208K ep:250 epch:62.42 loss:0.180 grdn:3.858 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:  80%|████████  | 16040/20000 [4:08:46<50:49,  1.30step/s]  INFO 2026-04-07 23:44:58 ot_train.py:439 step:26K smpl:208K ep:250 epch:62.46 loss:0.174 grdn:3.857 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  80%|████████  | 16060/20000 [4:09:04<49:57,  1.31step/s]  INFO 2026-04-07 23:45:17 ot_train.py:439 step:26K smpl:208K ep:250 epch:62.51 loss:0.174 grdn:4.200 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  80%|████████  | 16080/20000 [4:09:23<51:08,  1.28step/s]  INFO 2026-04-07 23:45:36 ot_train.py:439 step:26K smpl:209K ep:250 epch:62.56 loss:0.174 grdn:3.870 lr:1.0e-05 updt_s:0.125 data_s:0.827
Training:  80%|████████  | 16100/20000 [4:09:43<51:07,  1.27step/s]  INFO 2026-04-07 23:45:56 ot_train.py:439 step:26K smpl:209K ep:250 epch:62.61 loss:0.180 grdn:4.167 lr:1.0e-05 updt_s:0.125 data_s:0.856
Training:  81%|████████  | 16120/20000 [4:10:02<48:07,  1.34step/s]  INFO 2026-04-07 23:46:14 ot_train.py:439 step:26K smpl:209K ep:251 epch:62.66 loss:0.172 grdn:4.138 lr:1.0e-05 updt_s:0.135 data_s:0.799
Training:  81%|████████  | 16140/20000 [4:10:20<48:32,  1.33step/s]  INFO 2026-04-07 23:46:33 ot_train.py:439 step:26K smpl:209K ep:251 epch:62.70 loss:0.178 grdn:4.440 lr:1.0e-05 updt_s:0.124 data_s:0.803
Training:  81%|████████  | 16160/20000 [4:10:39<48:32,  1.32step/s]  INFO 2026-04-07 23:46:52 ot_train.py:439 step:26K smpl:209K ep:251 epch:62.75 loss:0.176 grdn:4.117 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  81%|████████  | 16180/20000 [4:10:58<45:27,  1.40step/s]  INFO 2026-04-07 23:47:10 ot_train.py:439 step:26K smpl:209K ep:251 epch:62.80 loss:0.175 grdn:4.172 lr:1.0e-05 updt_s:0.124 data_s:0.805
Training:  81%|████████  | 16200/20000 [4:11:16<47:01,  1.35step/s]  INFO 2026-04-07 23:47:28 ot_train.py:439 step:26K smpl:210K ep:251 epch:62.85 loss:0.177 grdn:4.644 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:  81%|████████  | 16220/20000 [4:11:35<47:55,  1.31step/s]  INFO 2026-04-07 23:47:47 ot_train.py:439 step:26K smpl:210K ep:252 epch:62.90 loss:0.179 grdn:3.886 lr:1.0e-05 updt_s:0.125 data_s:0.823
Training:  81%|████████  | 16240/20000 [4:11:53<43:33,  1.44step/s]INFO 2026-04-07 23:48:06 ot_train.py:439 step:26K smpl:210K ep:252 epch:62.94 loss:0.175 grdn:4.203 lr:1.0e-05 updt_s:0.125 data_s:0.803
Training:  81%|████████▏ | 16260/20000 [4:12:12<42:34,  1.46step/s]INFO 2026-04-07 23:48:24 ot_train.py:439 step:26K smpl:210K ep:252 epch:62.99 loss:0.178 grdn:3.943 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  81%|████████▏ | 16280/20000 [4:12:33<1:03:11,  1.02s/step]INFO 2026-04-07 23:48:46 ot_train.py:439 step:26K smpl:210K ep:252 epch:63.04 loss:0.179 grdn:4.148 lr:1.0e-05 updt_s:0.123 data_s:0.956
Training:  82%|████████▏ | 16300/20000 [4:12:51<1:01:06,  1.01step/s]INFO 2026-04-07 23:49:04 ot_train.py:439 step:26K smpl:210K ep:252 epch:63.09 loss:0.171 grdn:3.758 lr:1.0e-05 updt_s:0.124 data_s:0.779
Training:  82%|████████▏ | 16320/20000 [4:13:10<1:05:34,  1.07s/step]INFO 2026-04-07 23:49:23 ot_train.py:439 step:26K smpl:211K ep:253 epch:63.14 loss:0.181 grdn:3.927 lr:1.0e-05 updt_s:0.124 data_s:0.821
Training:  82%|████████▏ | 16340/20000 [4:13:29<1:12:33,  1.19s/step]INFO 2026-04-07 23:49:42 ot_train.py:439 step:26K smpl:211K ep:253 epch:63.18 loss:0.178 grdn:4.500 lr:1.0e-05 updt_s:0.124 data_s:0.837
Training:  82%|████████▏ | 16360/20000 [4:13:48<1:13:44,  1.22s/step]INFO 2026-04-07 23:50:01 ot_train.py:439 step:26K smpl:211K ep:253 epch:63.23 loss:0.173 grdn:4.110 lr:1.0e-05 updt_s:0.124 data_s:0.811
Training:  82%|████████▏ | 16380/20000 [4:14:06<1:11:30,  1.19s/step]INFO 2026-04-07 23:50:19 ot_train.py:439 step:26K smpl:211K ep:253 epch:63.28 loss:0.175 grdn:3.619 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  82%|████████▏ | 16400/20000 [4:14:26<1:14:34,  1.24s/step]INFO 2026-04-07 23:50:38 ot_train.py:439 step:26K smpl:211K ep:253 epch:63.33 loss:0.168 grdn:3.713 lr:1.0e-05 updt_s:0.123 data_s:0.833
Training:  82%|████████▏ | 16420/20000 [4:14:44<1:11:56,  1.21s/step]INFO 2026-04-07 23:50:57 ot_train.py:439 step:26K smpl:211K ep:254 epch:63.38 loss:0.177 grdn:4.109 lr:1.0e-05 updt_s:0.123 data_s:0.803
Training:  82%|████████▏ | 16440/20000 [4:15:02<1:09:36,  1.17s/step]INFO 2026-04-07 23:51:15 ot_train.py:439 step:26K smpl:212K ep:254 epch:63.42 loss:0.176 grdn:4.006 lr:1.0e-05 updt_s:0.123 data_s:0.784
Training:  82%|████████▏ | 16460/20000 [4:15:21<1:14:28,  1.26s/step]INFO 2026-04-07 23:51:33 ot_train.py:439 step:26K smpl:212K ep:254 epch:63.47 loss:0.173 grdn:3.760 lr:1.0e-05 updt_s:0.123 data_s:0.801
Training:  82%|████████▏ | 16480/20000 [4:15:39<1:09:55,  1.19s/step]INFO 2026-04-07 23:51:52 ot_train.py:439 step:26K smpl:212K ep:254 epch:63.52 loss:0.179 grdn:4.030 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  82%|████████▎ | 16500/20000 [4:15:58<1:03:46,  1.09s/step]INFO 2026-04-07 23:52:10 ot_train.py:439 step:26K smpl:212K ep:254 epch:63.57 loss:0.175 grdn:3.867 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  83%|████████▎ | 16520/20000 [4:16:16<1:05:19,  1.13s/step]INFO 2026-04-07 23:52:29 ot_train.py:439 step:27K smpl:212K ep:254 epch:63.62 loss:0.175 grdn:4.074 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  83%|████████▎ | 16540/20000 [4:16:35<1:12:14,  1.25s/step]INFO 2026-04-07 23:52:48 ot_train.py:439 step:27K smpl:212K ep:255 epch:63.66 loss:0.174 grdn:4.484 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  83%|████████▎ | 16560/20000 [4:16:54<1:11:00,  1.24s/step]INFO 2026-04-07 23:53:06 ot_train.py:439 step:27K smpl:212K ep:255 epch:63.71 loss:0.178 grdn:4.481 lr:1.0e-05 updt_s:0.124 data_s:0.807
Training:  83%|████████▎ | 16580/20000 [4:17:12<1:06:46,  1.17s/step]INFO 2026-04-07 23:53:24 ot_train.py:439 step:27K smpl:213K ep:255 epch:63.76 loss:0.170 grdn:3.864 lr:1.0e-05 updt_s:0.124 data_s:0.773
Training:  83%|████████▎ | 16600/20000 [4:17:30<1:08:23,  1.21s/step]INFO 2026-04-07 23:53:43 ot_train.py:439 step:27K smpl:213K ep:255 epch:63.81 loss:0.177 grdn:3.953 lr:1.0e-05 updt_s:0.123 data_s:0.792
Training:  83%|████████▎ | 16620/20000 [4:17:48<1:07:16,  1.19s/step]INFO 2026-04-07 23:54:01 ot_train.py:439 step:27K smpl:213K ep:255 epch:63.86 loss:0.170 grdn:4.066 lr:1.0e-05 updt_s:0.123 data_s:0.788
Training:  83%|████████▎ | 16640/20000 [4:18:07<1:13:51,  1.32s/step]INFO 2026-04-07 23:54:19 ot_train.py:439 step:27K smpl:213K ep:256 epch:63.90 loss:0.175 grdn:4.167 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  83%|████████▎ | 16660/20000 [4:18:26<1:15:07,  1.35s/step]INFO 2026-04-07 23:54:38 ot_train.py:439 step:27K smpl:213K ep:256 epch:63.95 loss:0.173 grdn:4.305 lr:1.0e-05 updt_s:0.123 data_s:0.808
Training:  83%|████████▎ | 16680/20000 [4:18:41<23:51,  2.32step/s]INFO 2026-04-07 23:54:53 ot_train.py:439 step:27K smpl:213K ep:256 epch:64.00 loss:0.176 grdn:3.569 lr:1.0e-05 updt_s:0.122 data_s:0.633
Training:  84%|████████▎ | 16700/20000 [4:19:03<1:06:38,  1.21s/step]INFO 2026-04-07 23:55:15 ot_train.py:439 step:27K smpl:214K ep:256 epch:64.05 loss:0.169 grdn:3.907 lr:1.0e-05 updt_s:0.125 data_s:0.985
Training:  84%|████████▎ | 16720/20000 [4:19:21<46:05,  1.19step/s]INFO 2026-04-07 23:55:34 ot_train.py:439 step:27K smpl:214K ep:256 epch:64.10 loss:0.178 grdn:4.275 lr:1.0e-05 updt_s:0.124 data_s:0.778
Training:  84%|████████▎ | 16740/20000 [4:19:39<38:21,  1.42step/s]INFO 2026-04-07 23:55:51 ot_train.py:439 step:27K smpl:214K ep:257 epch:64.14 loss:0.182 grdn:4.895 lr:1.0e-05 updt_s:0.124 data_s:0.769
Training:  84%|████████▍ | 16760/20000 [4:19:56<31:38,  1.71step/s]INFO 2026-04-07 23:56:09 ot_train.py:439 step:27K smpl:214K ep:257 epch:64.19 loss:0.179 grdn:4.187 lr:1.0e-05 updt_s:0.124 data_s:0.751
Training:  84%|████████▍ | 16780/20000 [4:20:14<29:04,  1.85step/s]INFO 2026-04-07 23:56:27 ot_train.py:439 step:27K smpl:214K ep:257 epch:64.24 loss:0.168 grdn:3.827 lr:1.0e-05 updt_s:0.125 data_s:0.775
Training:  84%|████████▍ | 16800/20000 [4:20:32<30:54,  1.73step/s]INFO 2026-04-07 23:56:45 ot_train.py:439 step:27K smpl:214K ep:257 epch:64.29 loss:0.175 grdn:4.060 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  84%|████████▍ | 16820/20000 [4:20:50<28:21,  1.87step/s]INFO 2026-04-07 23:57:03 ot_train.py:439 step:27K smpl:215K ep:257 epch:64.34 loss:0.177 grdn:4.122 lr:1.0e-05 updt_s:0.124 data_s:0.767
Training:  84%|████████▍ | 16840/20000 [4:21:08<29:39,  1.78step/s]INFO 2026-04-07 23:57:21 ot_train.py:439 step:27K smpl:215K ep:258 epch:64.38 loss:0.172 grdn:3.931 lr:1.0e-05 updt_s:0.124 data_s:0.776
Training:  84%|████████▍ | 16860/20000 [4:21:26<28:48,  1.82step/s]INFO 2026-04-07 23:57:39 ot_train.py:439 step:27K smpl:215K ep:258 epch:64.43 loss:0.177 grdn:4.400 lr:1.0e-05 updt_s:0.124 data_s:0.769
Training:  84%|████████▍ | 16880/20000 [4:21:44<27:41,  1.88step/s]INFO 2026-04-07 23:57:57 ot_train.py:439 step:27K smpl:215K ep:258 epch:64.48 loss:0.177 grdn:4.427 lr:1.0e-05 updt_s:0.126 data_s:0.778
Training:  84%|████████▍ | 16900/20000 [4:22:02<31:16,  1.65step/s]INFO 2026-04-07 23:58:15 ot_train.py:439 step:27K smpl:215K ep:258 epch:64.53 loss:0.168 grdn:3.879 lr:1.0e-05 updt_s:0.124 data_s:0.766
Training:  85%|████████▍ | 16920/20000 [4:22:19<28:25,  1.81step/s]INFO 2026-04-07 23:58:32 ot_train.py:439 step:27K smpl:215K ep:258 epch:64.58 loss:0.172 grdn:4.347 lr:1.0e-05 updt_s:0.125 data_s:0.744
Training:  85%|████████▍ | 16940/20000 [4:22:38<27:27,  1.86step/s]INFO 2026-04-07 23:58:50 ot_train.py:439 step:27K smpl:216K ep:258 epch:64.62 loss:0.173 grdn:3.561 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  85%|████████▍ | 16960/20000 [4:22:56<28:05,  1.80step/s]INFO 2026-04-07 23:59:08 ot_train.py:439 step:27K smpl:216K ep:259 epch:64.67 loss:0.173 grdn:4.099 lr:1.0e-05 updt_s:0.125 data_s:0.780
Training:  85%|████████▍ | 16980/20000 [4:23:14<28:04,  1.79step/s]INFO 2026-04-07 23:59:27 ot_train.py:439 step:27K smpl:216K ep:259 epch:64.72 loss:0.177 grdn:4.113 lr:1.0e-05 updt_s:0.124 data_s:0.786
Training:  85%|████████▌ | 17000/20000 [4:23:32<27:54,  1.79step/s]INFO 2026-04-07 23:59:45 ot_train.py:439 step:27K smpl:216K ep:259 epch:64.77 loss:0.169 grdn:4.059 lr:1.0e-05 updt_s:0.124 data_s:0.794
Training:  85%|████████▌ | 17020/20000 [4:23:51<27:20,  1.82step/s]INFO 2026-04-08 00:00:03 ot_train.py:439 step:27K smpl:216K ep:259 epch:64.82 loss:0.171 grdn:3.707 lr:1.0e-05 updt_s:0.124 data_s:0.790
Training:  85%|████████▌ | 17040/20000 [4:24:08<26:43,  1.85step/s]INFO 2026-04-08 00:00:21 ot_train.py:439 step:27K smpl:216K ep:259 epch:64.86 loss:0.179 grdn:4.196 lr:1.0e-05 updt_s:0.124 data_s:0.765
Training:  85%|████████▌ | 17060/20000 [4:24:26<26:06,  1.88step/s]INFO 2026-04-08 00:00:39 ot_train.py:439 step:27K smpl:216K ep:260 epch:64.91 loss:0.177 grdn:3.772 lr:1.0e-05 updt_s:0.125 data_s:0.755
Training:  85%|████████▌ | 17080/20000 [4:24:44<26:53,  1.81step/s]INFO 2026-04-08 00:00:57 ot_train.py:439 step:27K smpl:217K ep:260 epch:64.96 loss:0.173 grdn:3.842 lr:1.0e-05 updt_s:0.123 data_s:0.785
Training:  86%|████████▌ | 17100/20000 [4:25:03<41:23,  1.17step/s]INFO 2026-04-08 00:01:16 ot_train.py:439 step:27K smpl:217K ep:260 epch:65.01 loss:0.179 grdn:3.994 lr:1.0e-05 updt_s:0.122 data_s:0.839
Training:  86%|████████▌ | 17120/20000 [4:25:23<27:33,  1.74step/s]INFO 2026-04-08 00:01:35 ot_train.py:439 step:27K smpl:217K ep:260 epch:65.06 loss:0.177 grdn:3.802 lr:1.0e-05 updt_s:0.124 data_s:0.828
Training:  86%|████████▌ | 17140/20000 [4:25:42<27:43,  1.72step/s]INFO 2026-04-08 00:01:54 ot_train.py:439 step:27K smpl:217K ep:260 epch:65.10 loss:0.175 grdn:3.962 lr:1.0e-05 updt_s:0.124 data_s:0.825
Training:  86%|████████▌ | 17160/20000 [4:26:00<28:43,  1.65step/s]INFO 2026-04-08 00:02:13 ot_train.py:439 step:27K smpl:217K ep:261 epch:65.15 loss:0.171 grdn:3.933 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  86%|████████▌ | 17180/20000 [4:26:20<29:21,  1.60step/s]INFO 2026-04-08 00:02:32 ot_train.py:439 step:27K smpl:217K ep:261 epch:65.20 loss:0.179 grdn:4.128 lr:1.0e-05 updt_s:0.124 data_s:0.842
Training:  86%|████████▌ | 17200/20000 [4:26:39<31:05,  1.50step/s]INFO 2026-04-08 00:02:52 ot_train.py:439 step:27K smpl:218K ep:261 epch:65.25 loss:0.179 grdn:4.269 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  86%|████████▌ | 17220/20000 [4:26:58<29:43,  1.56step/s]INFO 2026-04-08 00:03:10 ot_train.py:439 step:27K smpl:218K ep:261 epch:65.30 loss:0.160 grdn:3.571 lr:1.0e-05 updt_s:0.135 data_s:0.812
Training:  86%|████████▌ | 17240/20000 [4:27:17<29:29,  1.56step/s]INFO 2026-04-08 00:03:29 ot_train.py:439 step:27K smpl:218K ep:261 epch:65.34 loss:0.172 grdn:4.212 lr:1.0e-05 updt_s:0.125 data_s:0.814
Training:  86%|████████▋ | 17260/20000 [4:27:36<30:36,  1.49step/s]INFO 2026-04-08 00:03:48 ot_train.py:439 step:27K smpl:218K ep:262 epch:65.39 loss:0.173 grdn:4.288 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  86%|████████▋ | 17280/20000 [4:27:54<30:52,  1.47step/s]INFO 2026-04-08 00:04:07 ot_train.py:439 step:27K smpl:218K ep:262 epch:65.44 loss:0.171 grdn:3.817 lr:1.0e-05 updt_s:0.124 data_s:0.796
Training:  86%|████████▋ | 17300/20000 [4:28:13<34:59,  1.29step/s]INFO 2026-04-08 00:04:26 ot_train.py:439 step:27K smpl:218K ep:262 epch:65.49 loss:0.171 grdn:3.509 lr:1.0e-05 updt_s:0.125 data_s:0.845
Training:  87%|████████▋ | 17320/20000 [4:28:33<34:29,  1.29step/s]INFO 2026-04-08 00:04:45 ot_train.py:439 step:27K smpl:219K ep:262 epch:65.54 loss:0.172 grdn:4.348 lr:1.0e-05 updt_s:0.125 data_s:0.834
Training:  87%|████████▋ | 17340/20000 [4:28:52<34:05,  1.30step/s]INFO 2026-04-08 00:05:04 ot_train.py:439 step:27K smpl:219K ep:262 epch:65.58 loss:0.172 grdn:4.394 lr:1.0e-05 updt_s:0.125 data_s:0.827
Training:  87%|████████▋ | 17360/20000 [4:29:10<32:39,  1.35step/s]INFO 2026-04-08 00:05:23 ot_train.py:439 step:27K smpl:219K ep:263 epch:65.63 loss:0.173 grdn:4.412 lr:1.0e-05 updt_s:0.126 data_s:0.813
Training:  87%|████████▋ | 17380/20000 [4:29:29<33:17,  1.31step/s]INFO 2026-04-08 00:05:42 ot_train.py:439 step:27K smpl:219K ep:263 epch:65.68 loss:0.166 grdn:4.112 lr:1.0e-05 updt_s:0.126 data_s:0.816
Training:  87%|████████▋ | 17400/20000 [4:29:48<34:05,  1.27step/s]INFO 2026-04-08 00:06:01 ot_train.py:439 step:27K smpl:219K ep:263 epch:65.73 loss:0.178 grdn:4.091 lr:1.0e-05 updt_s:0.125 data_s:0.825
Training:  87%|████████▋ | 17420/20000 [4:30:07<32:00,  1.34step/s]INFO 2026-04-08 00:06:20 ot_train.py:439 step:27K smpl:219K ep:263 epch:65.78 loss:0.173 grdn:3.948 lr:1.0e-05 updt_s:0.125 data_s:0.831
Training:  87%|████████▋ | 17440/20000 [4:30:26<31:36,  1.35step/s]INFO 2026-04-08 00:06:38 ot_train.py:439 step:27K smpl:220K ep:263 epch:65.82 loss:0.169 grdn:3.808 lr:1.0e-05 updt_s:0.124 data_s:0.797
Training:  87%|████████▋ | 17460/20000 [4:30:45<32:52,  1.29step/s]INFO 2026-04-08 00:06:57 ot_train.py:439 step:27K smpl:220K ep:263 epch:65.87 loss:0.175 grdn:4.178 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  87%|████████▋ | 17480/20000 [4:31:03<32:17,  1.30step/s]INFO 2026-04-08 00:07:16 ot_train.py:439 step:27K smpl:220K ep:264 epch:65.92 loss:0.180 grdn:4.473 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  88%|████████▊ | 17500/20000 [4:31:22<30:55,  1.35step/s]INFO 2026-04-08 00:07:35 ot_train.py:439 step:28K smpl:220K ep:264 epch:65.97 loss:0.182 grdn:4.430 lr:1.0e-05 updt_s:0.125 data_s:0.811
Training:  88%|████████▊ | 17520/20000 [4:31:41<36:21,  1.14step/s]INFO 2026-04-08 00:07:54 ot_train.py:439 step:28K smpl:220K ep:264 epch:66.01 loss:0.174 grdn:4.138 lr:1.0e-05 updt_s:0.125 data_s:0.831
Training:  88%|████████▊ | 17540/20000 [4:32:00<30:49,  1.33step/s]INFO 2026-04-08 00:08:13 ot_train.py:439 step:28K smpl:220K ep:264 epch:66.06 loss:0.172 grdn:3.760 lr:1.0e-05 updt_s:0.125 data_s:0.814
Training:  88%|████████▊ | 17560/20000 [4:32:19<33:12,  1.22step/s]INFO 2026-04-08 00:08:32 ot_train.py:439 step:28K smpl:220K ep:264 epch:66.11 loss:0.170 grdn:4.037 lr:1.0e-05 updt_s:0.125 data_s:0.825
Training:  88%|████████▊ | 17580/20000 [4:32:37<32:56,  1.22step/s]INFO 2026-04-08 00:08:50 ot_train.py:439 step:28K smpl:221K ep:265 epch:66.16 loss:0.173 grdn:4.176 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  88%|████████▊ | 17600/20000 [4:32:56<33:46,  1.18step/s]INFO 2026-04-08 00:09:08 ot_train.py:439 step:28K smpl:221K ep:265 epch:66.21 loss:0.172 grdn:3.706 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  88%|████████▊ | 17620/20000 [4:33:14<29:44,  1.33step/s]INFO 2026-04-08 00:09:26 ot_train.py:439 step:28K smpl:221K ep:265 epch:66.25 loss:0.169 grdn:4.355 lr:1.0e-05 updt_s:0.124 data_s:0.773
Training:  88%|████████▊ | 17640/20000 [4:33:32<30:41,  1.28step/s]INFO 2026-04-08 00:09:44 ot_train.py:439 step:28K smpl:221K ep:265 epch:66.30 loss:0.167 grdn:4.031 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:  88%|████████▊ | 17660/20000 [4:33:50<31:24,  1.24step/s]INFO 2026-04-08 00:10:03 ot_train.py:439 step:28K smpl:221K ep:265 epch:66.35 loss:0.164 grdn:3.691 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  88%|████████▊ | 17680/20000 [4:34:09<36:52,  1.05step/s]INFO 2026-04-08 00:10:22 ot_train.py:439 step:28K smpl:221K ep:266 epch:66.40 loss:0.175 grdn:3.976 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  88%|████████▊ | 17700/20000 [4:34:28<37:06,  1.03step/s]INFO 2026-04-08 00:10:41 ot_train.py:439 step:28K smpl:222K ep:266 epch:66.45 loss:0.169 grdn:3.892 lr:1.0e-05 updt_s:0.123 data_s:0.810
Training:  89%|████████▊ | 17720/20000 [4:34:47<44:15,  1.16s/step]INFO 2026-04-08 00:11:00 ot_train.py:439 step:28K smpl:222K ep:266 epch:66.49 loss:0.178 grdn:4.102 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  89%|████████▊ | 17740/20000 [4:35:06<48:00,  1.27s/step]INFO 2026-04-08 00:11:19 ot_train.py:439 step:28K smpl:222K ep:266 epch:66.54 loss:0.174 grdn:4.195 lr:1.0e-05 updt_s:0.123 data_s:0.829
Training:  89%|████████▉ | 17760/20000 [4:35:25<50:37,  1.36s/step]INFO 2026-04-08 00:11:37 ot_train.py:439 step:28K smpl:222K ep:266 epch:66.59 loss:0.170 grdn:4.092 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  89%|████████▉ | 17780/20000 [4:35:44<52:39,  1.42s/step]INFO 2026-04-08 00:11:56 ot_train.py:439 step:28K smpl:222K ep:267 epch:66.64 loss:0.171 grdn:3.910 lr:1.0e-05 updt_s:0.124 data_s:0.819
Training:  89%|████████▉ | 17800/20000 [4:36:02<50:10,  1.37s/step]INFO 2026-04-08 00:12:15 ot_train.py:439 step:28K smpl:222K ep:267 epch:66.69 loss:0.174 grdn:4.110 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  89%|████████▉ | 17820/20000 [4:36:20<47:59,  1.32s/step]INFO 2026-04-08 00:12:33 ot_train.py:439 step:28K smpl:223K ep:267 epch:66.73 loss:0.177 grdn:4.354 lr:1.0e-05 updt_s:0.125 data_s:0.770
Training:  89%|████████▉ | 17840/20000 [4:36:38<44:53,  1.25s/step]INFO 2026-04-08 00:12:51 ot_train.py:439 step:28K smpl:223K ep:267 epch:66.78 loss:0.176 grdn:4.412 lr:1.0e-05 updt_s:0.124 data_s:0.774
Training:  89%|████████▉ | 17860/20000 [4:36:56<41:39,  1.17s/step]INFO 2026-04-08 00:13:09 ot_train.py:439 step:28K smpl:223K ep:267 epch:66.83 loss:0.183 grdn:4.008 lr:1.0e-05 updt_s:0.123 data_s:0.781
Training:  89%|████████▉ | 17880/20000 [4:37:14<38:27,  1.09s/step]INFO 2026-04-08 00:13:27 ot_train.py:439 step:28K smpl:223K ep:268 epch:66.88 loss:0.176 grdn:4.122 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  90%|████████▉ | 17900/20000 [4:37:33<38:35,  1.10s/step]INFO 2026-04-08 00:13:45 ot_train.py:439 step:28K smpl:223K ep:268 epch:66.93 loss:0.166 grdn:3.977 lr:1.0e-05 updt_s:0.123 data_s:0.790
Training:  90%|████████▉ | 17920/20000 [4:37:51<41:44,  1.20s/step]INFO 2026-04-08 00:14:04 ot_train.py:439 step:28K smpl:223K ep:268 epch:66.97 loss:0.171 grdn:3.828 lr:1.0e-05 updt_s:0.124 data_s:0.815
Training:  90%|████████▉ | 17940/20000 [4:38:10<37:32,  1.09s/step]INFO 2026-04-08 00:14:23 ot_train.py:439 step:28K smpl:224K ep:268 epch:67.02 loss:0.183 grdn:4.632 lr:1.0e-05 updt_s:0.122 data_s:0.835
Training:  90%|████████▉ | 17960/20000 [4:38:30<36:43,  1.08s/step]INFO 2026-04-08 00:14:42 ot_train.py:439 step:28K smpl:224K ep:268 epch:67.07 loss:0.175 grdn:4.094 lr:1.0e-05 updt_s:0.124 data_s:0.830
Training:  90%|████████▉ | 17980/20000 [4:38:49<35:39,  1.06s/step]INFO 2026-04-08 00:15:02 ot_train.py:439 step:28K smpl:224K ep:268 epch:67.12 loss:0.172 grdn:3.925 lr:1.0e-05 updt_s:0.124 data_s:0.846
Training:  90%|█████████ | 18000/20000 [4:39:08<34:28,  1.03s/step]INFO 2026-04-08 00:15:21 ot_train.py:439 step:28K smpl:224K ep:269 epch:67.17 loss:0.173 grdn:3.680 lr:1.0e-05 updt_s:0.125 data_s:0.844
Training:  90%|█████████ | 18020/20000 [4:39:27<33:03,  1.00s/step]INFO 2026-04-08 00:15:40 ot_train.py:439 step:28K smpl:224K ep:269 epch:67.21 loss:0.180 grdn:4.187 lr:1.0e-05 updt_s:0.125 data_s:0.806
Training:  90%|█████████ | 18040/20000 [4:39:46<33:23,  1.02s/step]INFO 2026-04-08 00:15:58 ot_train.py:439 step:28K smpl:224K ep:269 epch:67.26 loss:0.166 grdn:3.730 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  90%|█████████ | 18060/20000 [4:40:04<33:07,  1.02s/step]INFO 2026-04-08 00:16:17 ot_train.py:439 step:28K smpl:224K ep:269 epch:67.31 loss:0.173 grdn:3.828 lr:1.0e-05 updt_s:0.124 data_s:0.806
Training:  90%|█████████ | 18080/20000 [4:40:23<33:51,  1.06s/step]INFO 2026-04-08 00:16:36 ot_train.py:439 step:28K smpl:225K ep:269 epch:67.36 loss:0.168 grdn:3.793 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  90%|█████████ | 18100/20000 [4:40:42<30:35,  1.04step/s]INFO 2026-04-08 00:16:55 ot_train.py:439 step:28K smpl:225K ep:270 epch:67.41 loss:0.170 grdn:3.796 lr:1.0e-05 updt_s:0.125 data_s:0.800
Training:  91%|█████████ | 18120/20000 [4:41:00<30:55,  1.01step/s]INFO 2026-04-08 00:17:13 ot_train.py:439 step:28K smpl:225K ep:270 epch:67.45 loss:0.173 grdn:4.171 lr:1.0e-05 updt_s:0.124 data_s:0.795
Training:  91%|█████████ | 18140/20000 [4:41:19<32:09,  1.04s/step]INFO 2026-04-08 00:17:32 ot_train.py:439 step:28K smpl:225K ep:270 epch:67.50 loss:0.168 grdn:3.863 lr:1.0e-05 updt_s:0.125 data_s:0.822
Training:  91%|█████████ | 18160/20000 [4:41:38<31:27,  1.03s/step]INFO 2026-04-08 00:17:50 ot_train.py:439 step:28K smpl:225K ep:270 epch:67.55 loss:0.168 grdn:3.934 lr:1.0e-05 updt_s:0.124 data_s:0.787
Training:  91%|█████████ | 18180/20000 [4:41:56<31:24,  1.04s/step]INFO 2026-04-08 00:18:09 ot_train.py:439 step:28K smpl:225K ep:270 epch:67.60 loss:0.171 grdn:3.621 lr:1.0e-05 updt_s:0.125 data_s:0.814
Training:  91%|█████████ | 18200/20000 [4:42:15<30:58,  1.03s/step]INFO 2026-04-08 00:18:28 ot_train.py:439 step:28K smpl:226K ep:271 epch:67.65 loss:0.169 grdn:3.678 lr:1.0e-05 updt_s:0.124 data_s:0.810
Training:  91%|█████████ | 18220/20000 [4:42:34<31:18,  1.06s/step]INFO 2026-04-08 00:18:46 ot_train.py:439 step:28K smpl:226K ep:271 epch:67.69 loss:0.165 grdn:3.759 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  91%|█████████ | 18240/20000 [4:42:53<30:15,  1.03s/step]INFO 2026-04-08 00:19:05 ot_train.py:439 step:28K smpl:226K ep:271 epch:67.74 loss:0.173 grdn:3.976 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  91%|█████████▏| 18260/20000 [4:43:11<28:41,  1.01step/s]INFO 2026-04-08 00:19:24 ot_train.py:439 step:28K smpl:226K ep:271 epch:67.79 loss:0.171 grdn:4.624 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  91%|█████████▏| 18280/20000 [4:43:30<28:46,  1.00s/step]INFO 2026-04-08 00:19:42 ot_train.py:439 step:28K smpl:226K ep:271 epch:67.84 loss:0.173 grdn:5.153 lr:1.0e-05 updt_s:0.125 data_s:0.805
Training:  92%|█████████▏| 18300/20000 [4:43:49<31:26,  1.11s/step]INFO 2026-04-08 00:20:01 ot_train.py:439 step:28K smpl:226K ep:272 epch:67.89 loss:0.179 grdn:4.350 lr:1.0e-05 updt_s:0.125 data_s:0.833
Training:  92%|█████████▏| 18320/20000 [4:44:08<28:27,  1.02s/step]INFO 2026-04-08 00:20:20 ot_train.py:439 step:28K smpl:227K ep:272 epch:67.93 loss:0.173 grdn:3.884 lr:1.0e-05 updt_s:0.136 data_s:0.807
Training:  92%|█████████▏| 18340/20000 [4:44:26<28:13,  1.02s/step]INFO 2026-04-08 00:20:39 ot_train.py:439 step:28K smpl:227K ep:272 epch:67.98 loss:0.176 grdn:4.056 lr:1.0e-05 updt_s:0.125 data_s:0.796
Training:  92%|█████████▏| 18360/20000 [4:44:48<41:21,  1.51s/step]INFO 2026-04-08 00:21:00 ot_train.py:439 step:28K smpl:227K ep:272 epch:68.03 loss:0.167 grdn:4.620 lr:1.0e-05 updt_s:0.124 data_s:0.962
Training:  92%|█████████▏| 18380/20000 [4:45:06<35:17,  1.31s/step]INFO 2026-04-08 00:21:19 ot_train.py:439 step:28K smpl:227K ep:272 epch:68.08 loss:0.172 grdn:4.180 lr:1.0e-05 updt_s:0.124 data_s:0.782
Training:  92%|█████████▏| 18400/20000 [4:45:24<30:40,  1.15s/step]INFO 2026-04-08 00:21:37 ot_train.py:439 step:28K smpl:227K ep:273 epch:68.13 loss:0.173 grdn:4.288 lr:1.0e-05 updt_s:0.124 data_s:0.780
Training:  92%|█████████▏| 18420/20000 [4:45:42<27:45,  1.05s/step]INFO 2026-04-08 00:21:55 ot_train.py:439 step:28K smpl:227K ep:273 epch:68.17 loss:0.168 grdn:4.311 lr:1.0e-05 updt_s:0.123 data_s:0.795
Training:  92%|█████████▏| 18440/20000 [4:46:01<21:37,  1.20step/s]INFO 2026-04-08 00:22:13 ot_train.py:439 step:28K smpl:228K ep:273 epch:68.22 loss:0.169 grdn:3.813 lr:1.0e-05 updt_s:0.124 data_s:0.784
Training:  92%|█████████▏| 18460/20000 [4:46:19<24:04,  1.07step/s]INFO 2026-04-08 00:22:32 ot_train.py:439 step:28K smpl:228K ep:273 epch:68.27 loss:0.174 grdn:4.293 lr:1.0e-05 updt_s:0.123 data_s:0.821
Training:  92%|█████████▏| 18480/20000 [4:46:38<23:29,  1.08step/s]INFO 2026-04-08 00:22:50 ot_train.py:439 step:28K smpl:228K ep:273 epch:68.32 loss:0.174 grdn:3.934 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  92%|█████████▎| 18500/20000 [4:46:56<23:01,  1.09step/s]INFO 2026-04-08 00:23:09 ot_train.py:439 step:28K smpl:228K ep:273 epch:68.37 loss:0.177 grdn:3.980 lr:1.0e-05 updt_s:0.124 data_s:0.801
Training:  93%|█████████▎| 18520/20000 [4:47:15<23:10,  1.06step/s]INFO 2026-04-08 00:23:28 ot_train.py:439 step:29K smpl:228K ep:274 epch:68.41 loss:0.181 grdn:4.602 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  93%|█████████▎| 18540/20000 [4:47:34<22:28,  1.08step/s]INFO 2026-04-08 00:23:47 ot_train.py:439 step:29K smpl:228K ep:274 epch:68.46 loss:0.165 grdn:3.807 lr:1.0e-05 updt_s:0.123 data_s:0.827
Training:  93%|█████████▎| 18560/20000 [4:47:53<22:34,  1.06step/s]INFO 2026-04-08 00:24:06 ot_train.py:439 step:29K smpl:228K ep:274 epch:68.51 loss:0.169 grdn:3.719 lr:1.0e-05 updt_s:0.124 data_s:0.822
Training:  93%|█████████▎| 18580/20000 [4:48:11<19:50,  1.19step/s]INFO 2026-04-08 00:24:24 ot_train.py:439 step:29K smpl:229K ep:274 epch:68.56 loss:0.177 grdn:4.309 lr:1.0e-05 updt_s:0.124 data_s:0.788
Training:  93%|█████████▎| 18600/20000 [4:48:30<18:24,  1.27step/s]INFO 2026-04-08 00:24:43 ot_train.py:439 step:29K smpl:229K ep:274 epch:68.61 loss:0.169 grdn:3.721 lr:1.0e-05 updt_s:0.123 data_s:0.808
Training:  93%|█████████▎| 18620/20000 [4:48:49<17:28,  1.32step/s]INFO 2026-04-08 00:25:02 ot_train.py:439 step:29K smpl:229K ep:275 epch:68.65 loss:0.166 grdn:3.986 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  93%|█████████▎| 18640/20000 [4:49:08<16:49,  1.35step/s]INFO 2026-04-08 00:25:21 ot_train.py:439 step:29K smpl:229K ep:275 epch:68.70 loss:0.173 grdn:4.361 lr:1.0e-05 updt_s:0.124 data_s:0.829
Training:  93%|█████████▎| 18660/20000 [4:49:27<16:42,  1.34step/s]INFO 2026-04-08 00:25:39 ot_train.py:439 step:29K smpl:229K ep:275 epch:68.75 loss:0.176 grdn:3.937 lr:1.0e-05 updt_s:0.125 data_s:0.804
Training:  93%|█████████▎| 18680/20000 [4:49:45<15:38,  1.41step/s]INFO 2026-04-08 00:25:57 ot_train.py:439 step:29K smpl:229K ep:275 epch:68.80 loss:0.171 grdn:3.669 lr:1.0e-05 updt_s:0.124 data_s:0.788
Training:  94%|█████████▎| 18700/20000 [4:50:03<16:44,  1.29step/s]INFO 2026-04-08 00:26:16 ot_train.py:439 step:29K smpl:230K ep:275 epch:68.85 loss:0.163 grdn:3.155 lr:1.0e-05 updt_s:0.125 data_s:0.797
Training:  94%|█████████▎| 18720/20000 [4:50:22<15:35,  1.37step/s]INFO 2026-04-08 00:26:34 ot_train.py:439 step:29K smpl:230K ep:276 epch:68.89 loss:0.164 grdn:4.026 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training:  94%|█████████▎| 18740/20000 [4:50:40<15:49,  1.33step/s]INFO 2026-04-08 00:26:53 ot_train.py:439 step:29K smpl:230K ep:276 epch:68.94 loss:0.171 grdn:3.688 lr:1.0e-05 updt_s:0.124 data_s:0.812
Training:  94%|█████████▍| 18760/20000 [4:50:59<14:54,  1.39step/s]INFO 2026-04-08 00:27:11 ot_train.py:439 step:29K smpl:230K ep:276 epch:68.99 loss:0.170 grdn:3.980 lr:1.0e-05 updt_s:0.124 data_s:0.791
Training:  94%|█████████▍| 18780/20000 [4:51:18<13:10,  1.54step/s]INFO 2026-04-08 00:27:30 ot_train.py:439 step:29K smpl:230K ep:276 epch:69.04 loss:0.174 grdn:4.041 lr:1.0e-05 updt_s:0.124 data_s:0.835
Training:  94%|█████████▍| 18800/20000 [4:51:37<14:54,  1.34step/s]INFO 2026-04-08 00:27:49 ot_train.py:439 step:29K smpl:230K ep:276 epch:69.09 loss:0.171 grdn:4.286 lr:1.0e-05 updt_s:0.123 data_s:0.825
Training:  94%|█████████▍| 18820/20000 [4:51:56<17:16,  1.14step/s]INFO 2026-04-08 00:28:08 ot_train.py:439 step:29K smpl:231K ep:277 epch:69.13 loss:0.169 grdn:4.202 lr:1.0e-05 updt_s:0.126 data_s:0.818
Training:  94%|█████████▍| 18840/20000 [4:52:15<17:47,  1.09step/s]INFO 2026-04-08 00:28:28 ot_train.py:439 step:29K smpl:231K ep:277 epch:69.18 loss:0.167 grdn:4.665 lr:1.0e-05 updt_s:0.124 data_s:0.849
Training:  94%|█████████▍| 18860/20000 [4:52:34<19:15,  1.01s/step]INFO 2026-04-08 00:28:47 ot_train.py:439 step:29K smpl:231K ep:277 epch:69.23 loss:0.169 grdn:4.267 lr:1.0e-05 updt_s:0.123 data_s:0.837
Training:  94%|█████████▍| 18880/20000 [4:52:53<18:29,  1.01step/s]INFO 2026-04-08 00:29:06 ot_train.py:439 step:29K smpl:231K ep:277 epch:69.28 loss:0.168 grdn:4.333 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  94%|█████████▍| 18900/20000 [4:53:12<16:00,  1.15step/s]INFO 2026-04-08 00:29:24 ot_train.py:439 step:29K smpl:231K ep:277 epch:69.33 loss:0.168 grdn:4.174 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  95%|█████████▍| 18920/20000 [4:53:30<16:20,  1.10step/s]INFO 2026-04-08 00:29:43 ot_train.py:439 step:29K smpl:231K ep:277 epch:69.37 loss:0.168 grdn:3.758 lr:1.0e-05 updt_s:0.123 data_s:0.815
Training:  95%|█████████▍| 18940/20000 [4:53:49<14:33,  1.21step/s]INFO 2026-04-08 00:30:01 ot_train.py:439 step:29K smpl:232K ep:278 epch:69.42 loss:0.172 grdn:4.007 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  95%|█████████▍| 18960/20000 [4:54:08<15:56,  1.09step/s]INFO 2026-04-08 00:30:20 ot_train.py:439 step:29K smpl:232K ep:278 epch:69.47 loss:0.173 grdn:4.023 lr:1.0e-05 updt_s:0.123 data_s:0.826
Training:  95%|█████████▍| 18980/20000 [4:54:27<15:26,  1.10step/s]INFO 2026-04-08 00:30:39 ot_train.py:439 step:29K smpl:232K ep:278 epch:69.52 loss:0.172 grdn:3.765 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  95%|█████████▌| 19000/20000 [4:54:45<13:33,  1.23step/s]INFO 2026-04-08 00:30:58 ot_train.py:439 step:29K smpl:232K ep:278 epch:69.57 loss:0.177 grdn:4.111 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  95%|█████████▌| 19020/20000 [4:55:04<12:33,  1.30step/s]INFO 2026-04-08 00:31:17 ot_train.py:439 step:29K smpl:232K ep:278 epch:69.61 loss:0.169 grdn:3.808 lr:1.0e-05 updt_s:0.124 data_s:0.832
Training:  95%|█████████▌| 19040/20000 [4:55:23<12:11,  1.31step/s]INFO 2026-04-08 00:31:35 ot_train.py:439 step:29K smpl:232K ep:279 epch:69.66 loss:0.166 grdn:4.067 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  95%|█████████▌| 19060/20000 [4:55:41<11:46,  1.33step/s]INFO 2026-04-08 00:31:54 ot_train.py:439 step:29K smpl:232K ep:279 epch:69.71 loss:0.174 grdn:3.966 lr:1.0e-05 updt_s:0.125 data_s:0.800
Training:  95%|█████████▌| 19080/20000 [4:56:00<12:27,  1.23step/s]INFO 2026-04-08 00:32:12 ot_train.py:439 step:29K smpl:233K ep:279 epch:69.76 loss:0.168 grdn:3.719 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  96%|█████████▌| 19100/20000 [4:56:18<12:34,  1.19step/s]INFO 2026-04-08 00:32:31 ot_train.py:439 step:29K smpl:233K ep:279 epch:69.81 loss:0.175 grdn:3.953 lr:1.0e-05 updt_s:0.124 data_s:0.814
Training:  96%|█████████▌| 19120/20000 [4:56:37<13:51,  1.06step/s]INFO 2026-04-08 00:32:50 ot_train.py:439 step:29K smpl:233K ep:279 epch:69.85 loss:0.171 grdn:3.855 lr:1.0e-05 updt_s:0.124 data_s:0.825
Training:  96%|█████████▌| 19140/20000 [4:56:57<15:06,  1.05s/step]INFO 2026-04-08 00:33:09 ot_train.py:439 step:29K smpl:233K ep:280 epch:69.90 loss:0.171 grdn:4.182 lr:1.0e-05 updt_s:0.123 data_s:0.835
Training:  96%|█████████▌| 19160/20000 [4:57:15<14:28,  1.03s/step]INFO 2026-04-08 00:33:27 ot_train.py:439 step:29K smpl:233K ep:280 epch:69.95 loss:0.169 grdn:3.793 lr:1.0e-05 updt_s:0.123 data_s:0.777
Training:  96%|█████████▌| 19180/20000 [4:57:33<13:53,  1.02s/step]INFO 2026-04-08 00:33:45 ot_train.py:439 step:29K smpl:233K ep:280 epch:70.00 loss:0.170 grdn:3.690 lr:1.0e-05 updt_s:0.122 data_s:0.789
Training:  96%|█████████▌| 19200/20000 [4:57:53<10:12,  1.31step/s]INFO 2026-04-08 00:34:05 ot_train.py:439 step:29K smpl:234K ep:280 epch:70.04 loss:0.173 grdn:4.213 lr:1.0e-05 updt_s:0.124 data_s:0.876
Training:  96%|█████████▌| 19220/20000 [4:58:11<09:44,  1.33step/s]INFO 2026-04-08 00:34:24 ot_train.py:439 step:29K smpl:234K ep:280 epch:70.09 loss:0.173 grdn:4.298 lr:1.0e-05 updt_s:0.125 data_s:0.810
Training:  96%|█████████▌| 19240/20000 [4:58:30<10:11,  1.24step/s]INFO 2026-04-08 00:34:43 ot_train.py:439 step:29K smpl:234K ep:281 epch:70.14 loss:0.172 grdn:3.950 lr:1.0e-05 updt_s:0.125 data_s:0.815
Training:  96%|█████████▋| 19260/20000 [4:58:48<09:55,  1.24step/s]INFO 2026-04-08 00:35:01 ot_train.py:439 step:29K smpl:234K ep:281 epch:70.19 loss:0.170 grdn:3.830 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:  96%|█████████▋| 19280/20000 [4:59:07<09:35,  1.25step/s]INFO 2026-04-08 00:35:19 ot_train.py:439 step:29K smpl:234K ep:281 epch:70.24 loss:0.173 grdn:4.266 lr:1.0e-05 updt_s:0.123 data_s:0.792
Training:  96%|█████████▋| 19300/20000 [4:59:25<09:16,  1.26step/s]INFO 2026-04-08 00:35:38 ot_train.py:439 step:29K smpl:234K ep:281 epch:70.28 loss:0.169 grdn:4.259 lr:1.0e-05 updt_s:0.123 data_s:0.801
Training:  97%|█████████▋| 19320/20000 [4:59:44<10:24,  1.09step/s]INFO 2026-04-08 00:35:57 ot_train.py:439 step:29K smpl:235K ep:281 epch:70.33 loss:0.164 grdn:4.096 lr:1.0e-05 updt_s:0.124 data_s:0.809
Training:  97%|█████████▋| 19340/20000 [5:00:02<09:43,  1.13step/s]INFO 2026-04-08 00:36:15 ot_train.py:439 step:29K smpl:235K ep:282 epch:70.38 loss:0.163 grdn:3.616 lr:1.0e-05 updt_s:0.123 data_s:0.803
Training:  97%|█████████▋| 19360/20000 [5:00:21<09:03,  1.18step/s]INFO 2026-04-08 00:36:34 ot_train.py:439 step:29K smpl:235K ep:282 epch:70.43 loss:0.166 grdn:4.307 lr:1.0e-05 updt_s:0.123 data_s:0.824
Training:  97%|█████████▋| 19380/20000 [5:00:40<07:59,  1.29step/s]INFO 2026-04-08 00:36:52 ot_train.py:439 step:29K smpl:235K ep:282 epch:70.48 loss:0.174 grdn:3.923 lr:1.0e-05 updt_s:0.123 data_s:0.794
Training:  97%|█████████▋| 19400/20000 [5:00:58<07:28,  1.34step/s]INFO 2026-04-08 00:37:11 ot_train.py:439 step:29K smpl:235K ep:282 epch:70.52 loss:0.171 grdn:3.801 lr:1.0e-05 updt_s:0.125 data_s:0.795
Training:  97%|█████████▋| 19420/20000 [5:01:17<07:21,  1.31step/s]INFO 2026-04-08 00:37:29 ot_train.py:439 step:29K smpl:235K ep:282 epch:70.57 loss:0.165 grdn:3.945 lr:1.0e-05 updt_s:0.124 data_s:0.798
Training:  97%|█████████▋| 19440/20000 [5:01:35<06:58,  1.34step/s]INFO 2026-04-08 00:37:48 ot_train.py:439 step:29K smpl:236K ep:282 epch:70.62 loss:0.174 grdn:4.083 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  97%|█████████▋| 19460/20000 [5:01:54<06:35,  1.37step/s]INFO 2026-04-08 00:38:06 ot_train.py:439 step:29K smpl:236K ep:283 epch:70.67 loss:0.165 grdn:3.779 lr:1.0e-05 updt_s:0.124 data_s:0.799
Training:  97%|█████████▋| 19480/20000 [5:02:12<06:32,  1.32step/s]INFO 2026-04-08 00:38:25 ot_train.py:439 step:29K smpl:236K ep:283 epch:70.72 loss:0.172 grdn:4.095 lr:1.0e-05 updt_s:0.124 data_s:0.816
Training:  98%|█████████▊| 19500/20000 [5:02:31<06:24,  1.30step/s]INFO 2026-04-08 00:38:44 ot_train.py:439 step:30K smpl:236K ep:283 epch:70.76 loss:0.169 grdn:3.694 lr:1.0e-05 updt_s:0.124 data_s:0.820
Training:  98%|█████████▊| 19520/20000 [5:02:49<05:46,  1.38step/s]INFO 2026-04-08 00:39:02 ot_train.py:439 step:30K smpl:236K ep:283 epch:70.81 loss:0.169 grdn:3.964 lr:1.0e-05 updt_s:0.125 data_s:0.783
Training:  98%|█████████▊| 19540/20000 [5:03:08<05:48,  1.32step/s]INFO 2026-04-08 00:39:21 ot_train.py:439 step:30K smpl:236K ep:283 epch:70.86 loss:0.169 grdn:3.731 lr:1.0e-05 updt_s:0.124 data_s:0.802
Training:  98%|█████████▊| 19560/20000 [5:03:27<05:44,  1.28step/s]INFO 2026-04-08 00:39:39 ot_train.py:439 step:30K smpl:236K ep:284 epch:70.91 loss:0.173 grdn:3.898 lr:1.0e-05 updt_s:0.134 data_s:0.796
Training:  98%|█████████▊| 19580/20000 [5:03:44<05:21,  1.31step/s]INFO 2026-04-08 00:39:57 ot_train.py:439 step:30K smpl:237K ep:284 epch:70.96 loss:0.171 grdn:4.081 lr:1.0e-05 updt_s:0.125 data_s:0.762
Training:  98%|█████████▊| 19600/20000 [5:04:06<12:09,  1.82s/step]INFO 2026-04-08 00:40:18 ot_train.py:439 step:30K smpl:237K ep:284 epch:71.00 loss:0.164 grdn:3.713 lr:1.0e-05 updt_s:0.122 data_s:0.945
Training:  98%|█████████▊| 19620/20000 [5:04:23<06:38,  1.05s/step]INFO 2026-04-08 00:40:36 ot_train.py:439 step:30K smpl:237K ep:284 epch:71.05 loss:0.170 grdn:3.449 lr:1.0e-05 updt_s:0.123 data_s:0.756
Training:  98%|█████████▊| 19640/20000 [5:04:41<06:53,  1.15s/step]INFO 2026-04-08 00:40:54 ot_train.py:439 step:30K smpl:237K ep:284 epch:71.10 loss:0.173 grdn:3.748 lr:1.0e-05 updt_s:0.124 data_s:0.776
Training:  98%|█████████▊| 19660/20000 [5:04:59<06:42,  1.18s/step]INFO 2026-04-08 00:41:12 ot_train.py:439 step:30K smpl:237K ep:285 epch:71.15 loss:0.165 grdn:3.678 lr:1.0e-05 updt_s:0.124 data_s:0.781
Training:  98%|█████████▊| 19680/20000 [5:05:17<05:33,  1.04s/step]INFO 2026-04-08 00:41:30 ot_train.py:439 step:30K smpl:237K ep:285 epch:71.20 loss:0.166 grdn:3.924 lr:1.0e-05 updt_s:0.123 data_s:0.765
Training:  98%|█████████▊| 19700/20000 [5:05:35<04:24,  1.13step/s]INFO 2026-04-08 00:41:48 ot_train.py:439 step:30K smpl:238K ep:285 epch:71.24 loss:0.162 grdn:3.666 lr:1.0e-05 updt_s:0.123 data_s:0.762
Training:  99%|█████████▊| 19720/20000 [5:05:52<03:20,  1.40step/s]INFO 2026-04-08 00:42:05 ot_train.py:439 step:30K smpl:238K ep:285 epch:71.29 loss:0.168 grdn:3.812 lr:1.0e-05 updt_s:0.124 data_s:0.751
Training:  99%|█████████▊| 19740/20000 [5:06:11<03:11,  1.36step/s]INFO 2026-04-08 00:42:23 ot_train.py:439 step:30K smpl:238K ep:285 epch:71.34 loss:0.170 grdn:4.253 lr:1.0e-05 updt_s:0.123 data_s:0.793
Training:  99%|█████████▉| 19760/20000 [5:06:29<02:51,  1.40step/s]INFO 2026-04-08 00:42:41 ot_train.py:439 step:30K smpl:238K ep:286 epch:71.39 loss:0.165 grdn:3.832 lr:1.0e-05 updt_s:0.123 data_s:0.781
Training:  99%|█████████▉| 19780/20000 [5:06:48<02:44,  1.33step/s]INFO 2026-04-08 00:43:00 ot_train.py:439 step:30K smpl:238K ep:286 epch:71.44 loss:0.168 grdn:3.969 lr:1.0e-05 updt_s:0.123 data_s:0.809
Training:  99%|█████████▉| 19800/20000 [5:07:06<02:26,  1.36step/s]INFO 2026-04-08 00:43:19 ot_train.py:439 step:30K smpl:238K ep:286 epch:71.48 loss:0.173 grdn:4.116 lr:1.0e-05 updt_s:0.124 data_s:0.793
Training:  99%|█████████▉| 19820/20000 [5:07:24<02:11,  1.36step/s]INFO 2026-04-08 00:43:37 ot_train.py:439 step:30K smpl:239K ep:286 epch:71.53 loss:0.169 grdn:3.795 lr:1.0e-05 updt_s:0.124 data_s:0.794
Training:  99%|█████████▉| 19840/20000 [5:07:42<01:56,  1.37step/s]INFO 2026-04-08 00:43:55 ot_train.py:439 step:30K smpl:239K ep:286 epch:71.58 loss:0.171 grdn:3.889 lr:1.0e-05 updt_s:0.124 data_s:0.770
Training:  99%|█████████▉| 19860/20000 [5:08:01<01:41,  1.39step/s]INFO 2026-04-08 00:44:13 ot_train.py:439 step:30K smpl:239K ep:287 epch:71.63 loss:0.167 grdn:3.631 lr:1.0e-05 updt_s:0.124 data_s:0.800
Training:  99%|█████████▉| 19880/20000 [5:08:19<01:26,  1.38step/s]INFO 2026-04-08 00:44:32 ot_train.py:439 step:30K smpl:239K ep:287 epch:71.68 loss:0.172 grdn:4.115 lr:1.0e-05 updt_s:0.124 data_s:0.789
Training: 100%|█████████▉| 19900/20000 [5:08:37<01:12,  1.37step/s]INFO 2026-04-08 00:44:49 ot_train.py:439 step:30K smpl:239K ep:287 epch:71.72 loss:0.167 grdn:3.744 lr:1.0e-05 updt_s:0.124 data_s:0.774
Training: 100%|█████████▉| 19920/20000 [5:08:55<00:58,  1.37step/s]INFO 2026-04-08 00:45:08 ot_train.py:439 step:30K smpl:239K ep:287 epch:71.77 loss:0.165 grdn:3.653 lr:1.0e-05 updt_s:0.125 data_s:0.775
Training: 100%|█████████▉| 19940/20000 [5:09:14<00:47,  1.27step/s]INFO 2026-04-08 00:45:26 ot_train.py:439 step:30K smpl:240K ep:287 epch:71.82 loss:0.171 grdn:3.873 lr:1.0e-05 updt_s:0.123 data_s:0.819
Training: 100%|█████████▉| 19960/20000 [5:09:32<00:30,  1.33step/s]INFO 2026-04-08 00:45:45 ot_train.py:439 step:30K smpl:240K ep:287 epch:71.87 loss:0.165 grdn:3.828 lr:1.0e-05 updt_s:0.124 data_s:0.783
Training: 100%|█████████▉| 19980/20000 [5:09:51<00:15,  1.30step/s]INFO 2026-04-08 00:46:03 ot_train.py:439 step:30K smpl:240K ep:288 epch:71.92 loss:0.164 grdn:3.641 lr:1.0e-05 updt_s:0.123 data_s:0.808
Training: 100%|██████████| 20000/20000 [5:10:09<00:00,  1.38step/s]INFO 2026-04-08 00:46:22 ot_train.py:439 step:30K smpl:240K ep:288 epch:71.96 loss:0.169 grdn:4.007 lr:1.0e-05 updt_s:0.124 data_s:0.797
INFO 2026-04-08 00:46:22 ot_train.py:459 Checkpoint policy after step 30000
Training: 100%|██████████| 20000/20000 [5:10:10<00:00,  1.07step/s]
INFO 2026-04-08 00:46:22 ot_train.py:533 End of training
