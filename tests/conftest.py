def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: mark test as slow (deselect with -m 'not slow')"
    )
