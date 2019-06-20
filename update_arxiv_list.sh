source activate py35
export PYTHONIOENCODING=utf8

git fetch --all
git reset --hard origin/master

//anaconda/envs/py35/bin/python create_group_arxiv_html.py 

git add .
git commit -m "synced @ $(date)"
git push
