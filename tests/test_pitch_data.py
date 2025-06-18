import pandas as pd
from mlb_data_lab.pitch_data import PitchData


def create_sample_csv(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "pitcher,pitch_type,release_speed,release_spin_rate,swing,whiff\n"
        "1,FF,95,2300,10,2\n"
        "1,SL,86,2500,5,1\n"
        "2,FF,96,2400,8,3\n"
    )
    return csv_file


def test_load(tmp_path):
    csv_file = create_sample_csv(tmp_path)
    data = PitchData(file_name=str(csv_file), data_dir="").load()
    assert len(data) == 3


def test_pitches_by_pitcher(tmp_path):
    csv_file = create_sample_csv(tmp_path)
    pd_obj = PitchData(file_name=str(csv_file), data_dir="")
    pd_obj.load()
    pitches = pd_obj.pitches_by_pitcher(1)
    assert len(pitches) == 2


def test_average_release_speed(tmp_path):
    csv_file = create_sample_csv(tmp_path)
    pd_obj = PitchData(file_name=str(csv_file), data_dir="")
    pd_obj.load()
    overall = pd_obj.average_release_speed()
    by_pitcher = pd_obj.average_release_speed(1)
    assert overall == pd_obj.data['release_speed'].mean()
    assert by_pitcher == 90.5


def test_summary_by_pitch_type(tmp_path):
    csv_file = create_sample_csv(tmp_path)
    pd_obj = PitchData(file_name=str(csv_file), data_dir="")
    summary = pd_obj.summary_by_pitch_type()
    assert set(summary['pitch_type']) == {"FF", "SL"}
