import os


def test_file_uses_supplied_uid_and_gid(tmp_path):
    test_file = tmp_path / "uid_gid_test_file"
    test_file.touch()

    file_stat = test_file.stat()
    assert file_stat.st_uid == int(os.environ["HOST_UID"])
    assert file_stat.st_gid == int(os.environ["HOST_GID"])
