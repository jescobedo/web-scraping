# Kettlebell Kings

I wanted to buy a kettlebell from [Kettlebell Kings](www.kettlebellkings.com), but they had such high demand during the Summer of 2020, that they would run out of stock very quickly after making some products available for purchase. While I signed up to receive restock notifications, I unfortunately never got any. So, I wrote a script that monitors the availability of the products I'm interested in, and sends me an SMS and email when they are back in stock.

To run the script:

1. Install the packages listed in `requirements.txt` (located in the parent folder), and create a virtual environment.
2. Fill in the missing info in `kettlebell_kings.ini`.
3. Run `kettlebell_kings.py` (modify some of the constants at the top of the file, if needed).