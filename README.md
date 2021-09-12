# surgelingo-backend
This is the backend of my submission for the Develop to Disrupt 2021 hackathon. You can view the frontend [here](https://develop-to-disrupt.devpost.com/).

## About SurgeLingo
_SurgeLingo_ addresses a fundamental issue that many language learners, especially beginner and intermediate ones, face: lack of comprehensible content. "Comprehensible content" is any form of audiovisual media that they can understand.

This submission solves that problem by creating a Twitter-esque feed of sentences in the learner's target language. These sentences are taken from the [Tatoeba database](https://tatoeba.org/en/), which has millions of sentences available for download, but they can also be user-contributed.

The radical new way in which SurgeLingo helps language learners 'surge ahead' in their studies is by:
- Sorting the sentences based off of difficulty.
- Allowing for different difficulties of sentences - from everything known for when the user is tired, to those where 70% of the content is known, and so on.
- Offering advanced sentence searching - by author, tags, content, and language - so that the user can learn sentences (or 'surges') in a field they are studying for.

And, of course, the truly killer feature - easy wordbank updating. In order to allow the user to seamlessly discover new 'surges', the application allows for a wealth of ways for the user to demonstrate their knowledge.

<img src="static/surgelingo_example.png" />

1. On the wordbank page, users can type in words they know, or paste from a frequency list. Future searches will use these words to calculate user knowledge.
2. An individual word in the result can be clicked to be added to the database.
3. To work at a faster pace, or for students who study sentence 'surges' in depth, the whole content can be marked as known.


## Stack
The frontend was built with Nuxt and Vue 2. TailwindCSS was used for styling, and the modules `nuxt-auth` and `nuxt-axios` were used for smooth user authentication and requests to the backend.

The backend was built with the Flask Python microframework, and used a PostgreSQL database to store user info, surges, and so on.

The `nltk` Python package, a natural language processing library, was leveraged so that surge sentences and user wordbanks would be [stemmed](https://en.wikipedia.org/wiki/Stemming), a process that reduces the words inside to their root form. This allowed for support of languages that have conjugation. A number of other packages that extend Flask or allow for content generation were also used.
