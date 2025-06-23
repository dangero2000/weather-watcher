# Notice:

This project is entirely constructed using Chat GPT. I wanted this script ASAP for my own private use, and was not originally intending to post it anywhere. However, I decided to post it anyway, figuring people might get some use out of it. Therefore, please don't expect any ground-breaking code here. Pull requests are absolutely welcome.

# Inspiration

Two things inspired me, actually.

- There is a YouTube channel called [Ryan Hall, Y'all](https://www.youtube.com/@RyanHallYall), that does live weather coverage as it's happening. In their latest video, ([The June 20-21, 2025 Severe Weather Coverage, As It Happened...](https://www.youtube.com/live/XsLKrlZLj5Q)), Ryan showcased a bot that announces weather info.
- On April 28, 2025, [Liam Erven](https://www.youtube.com/@liamerven) unvailed [his chat bot](https://www.youtube.com/watch?v=QM8bJqGJrqI) which summerizes a preset number of chat messages.

This gave me the idea of making my own script to summerize weather events every hour on the hour on my private AzuraCast station. Originally, I was going to have the script live stream to the station directly via the Icecast relay, but I was having trouble getting Chat GPT to give me a working script. Instead, I had it configured to get weather alerts two minutes before the hour,, then upload the audio via SFTP. By the time my weather playlist came on, the new files would play, giving off the elusion of a live broadcast.

  # To do List

- [ ] Stop Gemini from announcing mondain weather events
- [ ] Add support for multiple AI providers
- [ ] Add support for multiple TTS providers
- [ ] Add cross-platform support
- [ ] Add support for AI providers to change TTS voices on the fly
- [ ] Rewrite the entire code base to not depend on Chat GPT
