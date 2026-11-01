# ecommerce
building ecommerce site

# frontend cmd to run
python3 -m http.server 5500

# enter into postgres
sudo -u postgres psql -d ecommerce

view tables: \dt

view table schema: \d table_name

# test commands

uv run pytest ----> for all test
uv run pytest tests/integration/test_cart.py -v ----> for single test file 
uv run pytest -x -v ------> To stop at the first failure

