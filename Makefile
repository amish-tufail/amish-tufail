.PHONY: all stats art clean
all: art

stats:            ## refresh stats.json from the GitHub API (needs `gh` logged in)
	python3 build/fetch_stats.py

art:              ## rebuild every SVG and README.md from the current stats.json
	python3 build/build.py
	python3 build/readme.py

clean:
	rm -rf assets build/__pycache__
