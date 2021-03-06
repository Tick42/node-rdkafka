{
  "variables": {
    # may be redefined in command line on configuration stage
    # "BUILD_LIBRDKAFKA%": "<!(echo ${BUILD_LIBRDKAFKA:-1})"
    "BUILD_LIBRDKAFKA%": "<!(node ./util/get-env.js BUILD_LIBRDKAFKA 1)",
  },
  "targets": [
    {
      "target_name": "<(module_name)",
      'sources': [
        'src/binding.cc',
        'src/callbacks.cc',
        'src/common.cc',
        'src/config.cc',
        'src/connection.cc',
        'src/errors.cc',
        'src/kafka-consumer.cc',
        'src/producer.cc',
        'src/topic.cc',
        'src/workers.cc',
        'src/admin.cc'
      ],
      "include_dirs": [
        "<!(node -e \"require('nan')\")",
        "<(module_root_dir)/"
      ],
      'conditions': [
        [
          'OS=="win"',
          {
            'actions': [
              {
                'action_name': 'nuget_librdkafka_download',
                'inputs': [
                  'deps/windows-install.py'
                ],
                'outputs': [
                  'deps/precompiled/librdkafka.lib',
                  'deps/precompiled/librdkafkacpp.lib'
                ],
                'message': 'Getting librdkafka from nuget',
                'action': ['python', '<@(_inputs)']
              }
            ],
            'cflags_cc' : [
              '-std=c++11'
            ],
            'msvs_settings': {
              'VCLinkerTool': {
                'AdditionalDependencies': [
                  'librdkafka.lib',
                  'librdkafkacpp.lib'
                ],
                'AdditionalLibraryDirectories': [
                  '../deps/precompiled/'
                ]
              },
              'VCCLCompilerTool': {
                'AdditionalOptions': [
                  '/GR'
                ],
                'AdditionalUsingDirectories': [
                  'deps/precompiled/'
                ],
                'AdditionalIncludeDirectories': [
                  'deps/librdkafka/src',
                  'deps/librdkafka/src-cpp'
                ]
              }
            },
            'msvs_version': '2017',
            'msbuild_toolset': 'v141',
            'include_dirs': [
              'deps/include'
            ]
          },
          {
            'conditions': [
              [ "<(BUILD_LIBRDKAFKA)==1",
                {
                  "dependencies": [
                    "deps/librdkafka.gyp:librdkafka"
                  ],
                  "include_dirs": [
                    "deps/librdkafka/src",
                    "deps/librdkafka/src-cpp"
                  ],
                  'conditions': [
                    [
                      'OS=="linux"',
                      {
                        "libraries": [
                          "../build/deps/librdkafka.so",
                          "../build/deps/librdkafka++.so",
                          "-Wl,-rpath='$$ORIGIN/../deps'",
                        ],
                      }
                    ],
                    [
                      'OS=="mac"',
                      {
                        "libraries": [
                          "../build/deps/librdkafka.dylib",
                          "../build/deps/librdkafka++.dylib",
                        ],
                      }
                    ]
                  ],
                },
                # Else link against globally installed rdkafka and use
                # globally installed headers.  On Debian, you should
                # install the librdkafka1, librdkafka++1, and librdkafka-dev
                # .deb packages.
                {
                  "libraries": ["-lrdkafka", "-lrdkafka++"],
                  "include_dirs": [
                    "/usr/include/librdkafka",
                    "/usr/local/include/librdkafka",
                    "/opt/include/librdkafka",
                  ],
                },
              ],
              [
                'OS=="linux"',
                {
                  'cflags_cc' : [
                    '-std=c++11'
                  ],
                  'cflags_cc!': [
                    '-fno-rtti'
                  ]
                }
              ],
              [
                'OS=="mac"',
                {
                  'xcode_settings': {
                    'MACOSX_DEPLOYMENT_TARGET': '10.11',
                    'GCC_ENABLE_CPP_RTTI': 'YES',
                    'OTHER_LDFLAGS': [
                      '-L/usr/local/opt/openssl/lib'
                    ],
                    'OTHER_CPLUSPLUSFLAGS': [
                      '-I/usr/local/opt/openssl/include',
                      '-std=c++11'
                    ],
                  },
                }
              ]
            ]
          }
        ]
      ]
    },
    {
      "target_name": "copy-module",
      "type": "none",
      "dependencies": [ "<(module_name)" ],
      "copies": [
        {
          "files": [ "<(PRODUCT_DIR)/<(module_name).node"],
          "destination": "<(module_path)"
        }
      ]
    },
    {
      "target_name": "copy-libs",
      "type": "none",
      "dependencies": [ "<(module_name)" ],
      "conditions": [
        ['OS=="win"', {
          "copies": [{
            "destination": "<(module_path)",
            "files": [
              "<(PRODUCT_DIR)/librdkafka.dll",
              "<(PRODUCT_DIR)/librdkafkacpp.dll",
              "<(PRODUCT_DIR)/zlib.dll",
              "<(PRODUCT_DIR)/libzstd.dll",
              "<(PRODUCT_DIR)/msvcp120.dll",
              "<(PRODUCT_DIR)/msvcr120.dll"
            ]
          }]
        }],
        [ "<(BUILD_LIBRDKAFKA)==1", {
          "copies": [{
            "destination": "<(module_path)",
            "conditions": [
              ['OS=="linux"', {
                "files": [
                    "build/deps/librdkafka.so.1",
                    "build/deps/librdkafka++.so.1"
                  ]
              }],
              ['OS=="mac"', {
                "files": [
                    "build/deps/librdkafka.dylib",
                    "build/deps/librdkafka++.dylib"
                  ]
              }]
            ]
          }]
        }]
      ]
    }
  ]
}
