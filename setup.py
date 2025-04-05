from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mlb_stats",
    version="0.1.0",  # Update version as needed
    author="Timothy Fisher",
    author_email="timothyf@gmail.com",
    description="A Python application for generating advanced stat summary sheets for MLB players and teams.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timothyf/mlb_stats",  # Replace with your GitHub repository URL
    packages=find_packages(),  # Automatically find packages in the project
    include_package_data=True,
    install_requires=[
        "pandas==2.2.3",
        "numpy==2.1.1",
        "matplotlib==3.9.2",
        "seaborn==0.13.2",
        "mplcursors==0.5.3",
        "pybaseball==2.2.7",
        "MLB-StatsAPI==1.7.2",
        "requests==2.32.3",
        "python-dotenv==1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        'Topic :: Software Development :: Libraries',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Data Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Games/Entertainment :: Sports",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",  # Specify the minimum Python version required
    entry_points={
        "console_scripts": [
            "generate-player-summary=mlb_stats.scripts.generate_player_summary:main",
            "generate-team-summary=mlb_stats.scripts.generate_team_summary:main",
            "save_fangraphs_leaderboards=mlb_stats.scripts.save_fangraphs_leadersboards:main",
            "save-statcast-data=mlb_stats.scripts.save_statcast_data:main",
        ],
    },
)
