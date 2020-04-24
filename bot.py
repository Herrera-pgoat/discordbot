import os
from os import path
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
server = os.getenv('DISCORD_GUILD')

#client = discord.Client()
#right here I am telling that every command starts with !
#and telling it that the commaonds are case insensitive so they can type in any way of the command in terms of casing and it will work.
bot = discord.ext.commands.Bot(command_prefix="!",case_insensitive=True)

#This basically tells us that every time we connect to the discord server we print in python that we have connected to the discord server
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

#Here we only enter when the name is in there
@bot.command(name='pot', help='!pot returns potato')
async def pot(ctx):
    await ctx.send('potato')
    await ctx.send('second potato')

#We only enter here when the name is there
@bot.command(name='pin', help="!pin <message> pins the message to the pin thing in chat")
async def pin(ctx, *args):
    #args has everythin after the command
    #getting all the arguments and joining them together with a spacebar and putting it in content
    content = ' '.join(args)
    message = await ctx.send( (content) )
    await message.pin()
    #content = ' '.join(args)
    #await ctx.send(content)

@bot.command(name='top', help="!top <number> returns the numberth pin to the chat. If no number then just top pin")
async def top(ctx, *args):
    #Top tells us to get the top Pin
    pinNum = 0
    #checking if they gave an argument and if it is numberic
    if len(args) == 1 and args[0].isnumeric():
        pinNum = int(args[0]) -  1
    #this gets us all the pins that the
    allPinned = await ctx.author.pins()
    allChannels = ctx.guild.channels
    theChannel = 0
    for channel in allChannels:
        if channel.name =='general':
            theChannel = channel
    #I now have the channel that I want
    pinnedMessages = await theChannel.pins()
    if len(pinnedMessages) < pinNum:
        await ctx.send('We do not have that many pinned messages')
    else:
        await ctx.send(pinnedMessages[pinNum].content)

@bot.command( help='!gold <name> If you do not provide a name you will see the list of golds. If you do then you will add a gold.')
async def gold(ctx,*args):
    #we are getting all the database stuff
    engine = create_engine('sqlite:///society.db')

    from models import Person

    Session = sessionmaker(bind=engine)
    session = Session()

    if (len(args) == 0):
        content = ' '
        for name in session.query(Person.name):
            content = content + (name.name) + '\n'
        await ctx.send(content)
    else:
        #there are arguments so we add the gold
        newGold = ' '.join(args)
        gold = Person(color='Gold',name=newGold)
        session.add(gold)
        session.commit()
        await ctx.send( ('Added: '+ newGold) )
    #we are closing the session.
    session.close()

@bot.command( help='!book <title> returns information about title of the book. If there is no title provided then return current book information')
async def book(ctx, *args):
    #we are getting all the database stuff
    engine = create_engine('sqlite:///society.db')

    from models import BookRead

    Session = sessionmaker(bind=engine)
    session = Session()

    #if they just want to current book that is being read with the description and purchase info
    if (len(args) == 0):
        currentBook = session.query(BookRead).filter_by(currBook = True).first()
        await ctx.send(currentBook)
    #returns the book title and description and the purchase info for that book
    else:
        #getting the title of the book
        bookTitle = ' '.join(args)
        #getting all the information for the book they are going to read
        book = session.query(BookRead).filter_by(title = bookTitle).first()
        await ctx.send(book)
    session.close()

#command that will return all the books we have read for book club
@bot.command( help='!books <dm> returns all the books we have read in the book club. If you include word dm then it will be dmed to you rather than in the chat')
async def books(ctx, *args):
    #getting the db stuff
    engine = create_engine('sqlite:///society.db')
    from models import BookRead
    Session = sessionmaker(bind = engine)
    session = Session()

    allBooks = session.query(BookRead)
    arg1 =' '
    if(len(args) >=1):
        arg1 = args[0]
    if arg1.lower() == 'dm':
        for book in allBooks:
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send(book)
    #they have elected not to put it as a dm so it will be in chat
    else:
        for book in allBooks:
            await ctx.send(book)

#command that adds a book to the reading thing
@bot.command( help='!reading <title> adds this book to the BookRead table ')
async def reading(ctx, *args):
    if (len(args)==0):
        await ctx.send('You need to provide a title for the book we are going to read. Try !help reading ')
        return

    if ctx.author.permissions_in(ctx.message.channel).administrator:
        #we are getting all the database stuff
        engine = create_engine('sqlite:///society.db')
        from models import BookRead
        Session = sessionmaker(bind=engine)
        session = Session()
        #getting the book title from the args
        bookTitle = ' '.join(args)
        #adding that book to the Bookreading table and setting it as the currentBook
        newBook = BookRead(title = bookTitle,currBook=True )
        session.add(newBook)
        session.commit()
        session.close()
        await ctx.send( ('Added book as the current book we are reading: ' + bookTitle ) )
    else:
        await ctx.send('You must be an admin to add a new book we are reading')

#command that adds a book to the reading thing
@bot.command( help='!description <title> // <description> adds a description to a book with this title. Is separated by a literal // . Space after title and before description. ')
async def description(ctx, *args):
    #we are getting all the database stuff
    if (len(args)==0):
        await ctx.send('You need to provide a title for the book. Try !help description ')
        return

    if ctx.author.permissions_in(ctx.message.channel).administrator:
        #still getting the database stuff
        engine = create_engine('sqlite:///society.db')
        from models import BookRead
        Session = sessionmaker(bind=engine)
        session = Session()

        #we are searching for the index where // is
        index = 0
        for word in args:
            print(word)
            if word == '//':
                break
            index +=1

        #For args I need to search for the / then when I find it I add everything before it to the book title
        #and everything after to the description
        bookTitle = ' '.join(args[0:index])
        bookDescription = ' '.join(args[(index+1):])

        #getting the row for the place that matches the book we are reading
        bookReading = session.query(BookRead).filter_by(title = bookTitle).first()
        #changing what the description is for the book
        bookReading.description = bookDescription
        #committing the changes for the database and
        session.commit()
        session.close()
        await ctx.send( ('{} has a description now: '.format(bookTitle) ) )
    else:
        await ctx.send("You must be an admin to add a description to the book we are reading")

#command that adds a book to the reading thing
@bot.command( help='!purchase <title> // <purchase info> adds a description to a book with this title. Is separated by a literal // there needs to be a spaces like in the example. ')
async def purchase(ctx, *args):
    #we are getting all the database stuff
    if (len(args)==0):
        await ctx.send('You need to provide a title for the book. Try !help purchase ')
        return

    #You must be an admin to issue this command
    if ctx.author.permissions_in(ctx.message.channel).administrator:
        #getting the db stuff
        engine = create_engine('sqlite:///society.db')
        from models import BookRead
        Session = sessionmaker(bind=engine)
        session = Session()

        #we are searching for the index where // is
        index = 0
        for word in args:
            print(word)
            if word == '//':
                break
            index +=1

        #For args I need to search for the / then when I find it I add everything before it to the book title
        #and everything after is the purchas info
        bookTitle = ' '.join(args[0:index])
        bookPurchase = ' '.join(args[(index+1):])

        #getting the row for the place that matches the book we are reading
        bookReading = session.query(BookRead).filter_by(title = bookTitle).first()
        #changing what the description is for the book
        bookReading.purchaseInfo = bookPurchase
        #committing the changes for the database and
        session.commit()
        session.close()
        await ctx.send( ('{} has its purchase info now: '.format(bookTitle) ) )
    else:
        await ctx.send('You must be an admin to add purchase info.')

@bot.command(help="!finished <title> makes the book with that title a finished book")
async def finished(ctx,*args):
    if (len(args) == 0):
        await ctx.send('Use !help finished to learn to use this command')
        return
    else:
        #doing the database things
        if( if ctx.author.permissions_in(ctx.message.channel).administrator):
            engine = create_engine('sqlite:///society.db')
            from models import BookRead
            Session = sessionmaker(bind=engine)
            session = Session()

            #title of the book
            bookTitle = ' '.join(args)
            #getting the book
            book = session.query(BookRead).filter_by(title=bookTitle).first()

            #we enter this if statement if we could not find the book
            if book is None:
                await ctx.send('We could not find a book with title: {}'.format(bookTitle))
                return
            #we enter here if we do find a book with that title
            else:
                book.currBook = False
                await ctx.send('We have finished book {}'.format(bookTitle))
                session.commit()
            session.close()
        else:
            await ctx.send("You must be an admin to issue this command ")

@bot.command(help='!hw <description> without the description you get what reading is due next. With description it updates the description')
async def hw(ctx,*args):
    #if hw is already here
    if (path.exists('hw.txt')):
        #deciding whether we are updating description or reading what is next due
        if (len(args) != 0 )  :
            if ctx.author.permissions_in(ctx.message.channel).administrator:
                print ( ctx.author.permissions_in(ctx.message.channel).administrator)
                hw = open('hw.txt','w')
                content = ' '.join(args)
                hw.write(content)
                await ctx.send('Updated reading')
                hw.close()
            else:
                await ctx.send('You are not an admin. You cannnot make an update. Sorry :(')
        else:
            hw = open('hw.txt','r')
            content = hw.read()
            await ctx.send(content)
            hw.close()
    #here we are making the hw file
    else:
        hw = open('hw.txt','w')
        hw.write('Next reading is going to be here')
        hw.close()
        await ctx.send('Next reading is going to be here')

@bot.command(help='!considering . Prints the list of book considering.')
async def considering(ctx):
    #getting the book list
    engine = create_engine('sqlite:///society.db')
    from models import BookList
    Session = sessionmaker(bind=engine)
    session = Session()
    consideringBooks = session.query(BookList)
    for book in consideringBooks:
        await ctx.send(book)

@bot.command(help="!remove <title> . Removes this book from the books we are considering.")
async def remove(ctx, *args):
    if (len(args) == 0):
        await ctx.send('Try using !help remove to learn how to properly use it.')
    else:
        #getting the book list
        engine = create_engine('sqlite:///society.db')
        from models import BookList
        Session = sessionmaker(bind=engine)
        session = Session()
        book = session.query(BookList).filter_by(title = ' '.join(args)).first()
        if(book is None):
            await ctx.send('Could not find book with title: {}\nCheck out the spelling again!'.format(' '.join(args)))
        else:
            session.delete(book)
            session.commit()
            await ctx.send('We have removed that book')
        session.close()


@bot.command(help="!consider <title> // <description> . Adds this book to the books we are considering list. You don't need to put a description")
async def consider(ctx, *args):
    if (len(args) == 0):
        await ctx.send('Try using !help consider for some help')
    else:
        #getting the book list
        engine = create_engine('sqlite:///society.db')
        from models import BookList
        Session = sessionmaker(bind=engine)
        session = Session()
        #we are searching for the index where // is
        index = 0
        for word in args:
            if word == '//':
                break
            index +=1

        #getting the bookTitle along with the book description
        bookTitle = ' '.join(args[0:index])
        bookDescription = ' '.join(args[index+1:])
        if(index == -1):
            bookDescription = 'No description for the book.'

        #adding the book we want to consider for the reading
        considerBook = BookList(title=bookTitle,description=bookDescription)
        session.add(considerBook)
        session.commit()
        session.close()
        await ctx.send('You have added {} for consideration in the book club'.format(bookTitle))

    #this is when I was keeping track of stuff with a textfile rather than a database
    # if( path.exists('gold.txt')):
    #     #if there are no arguemnts we just read the list of golds
    #     if (len(args) == 0):
    #         gold = open('gold.txt','r')
    #         content = ''
    #         for line in gold:
    #             content += line
    #         await ctx.send(content)
    #
    #     #otherwise there are arguments so we add the gold
    #     else:
    #         newGold = ' '.join(args)
    #         gold = open('gold.txt','a')
    #         gold.write( ( newGold +'\n') )
    #         gold.close()
    #         await ctx.send( ('Added: ' + newGold )  )
    #
    # #we enter here if the file does not exists
    # else:
    #     gold = open('gold.txt','w')
    #     gold.write('Darrow Lykos\n')
    #     if len(args) == 0:
    #         await ctx.send('Added: Darrow Lykos as gold')
    #     else:
    #         gold.write(' '.join(args))

print(server)
bot.run(TOKEN)
