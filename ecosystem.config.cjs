module.exports = {
  apps: [
    {
      name: 'snts',
      script: 'run.py',
      interpreter: 'python3',
      cwd: '/home/user/snts',
      env: {
        FLASK_ENV: 'development',
        FLASK_DEBUG: '0',
        PORT: '5000'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 5,
    }
  ]
};
