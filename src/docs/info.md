*Welcome to LibertatemX project*

* === WHAT IS IT? === *

Nobody likes censorship, but people don't like to hear many things also. How we can find what should be public and what shouldn't?
Laws and rules based on violence work quite bad if they work at all.
LibertatemX is prototype of crypto-democracy. It has 2 parts - channel @libertatemx and bot @LibertatemXBot.
Everybody can post any message to channel, no any limits or censorship.
And only subscribers can decide which messages will stay and which will be deleted. Subscribers vote with money, I believe this is type of voting is the fairest.
We use here only [ethereum](https://ethereum.org) for payments for now.

* === HOW IT WORKS? === *

[/post](/post) - command to create new post in channel. You can use arguments:
*/post anon* - your name will not be connected with post in our db, so nobody can know who did it, but you can't withdraw money from post's balance

*/post forward* - your messge will be forwarded, your name will be showed in channel

Send command, wait answer of bot and type you message, send it and you'll receive ethereum address where you need to send any amount of ethereum.
After payment is confirmed your message will be posted in channel. All money you sent will be on post's balance.

[/withdraw](/withdraw) - command to withdraw money from post's balance.
Only author of post can do it, if _he didn't post the message anonymously_.
If post's balance equals 0, post will be deleted. So don't withdraw last money from your post if you don't want to delete it.

[/like](/like) - command to like some post, it can has argument:
*/like anon* - your name will not be saved in db and nobody will know who did that like
You'll receive short description of last 10 posts and you need to choice which one you like.
After that you'll receive ethereum address where you need to send any amount of ethereum depends how much you liked the message.
This money will go to post's balance and author will be able to wthdraw, so like is physical thanks for post.

[/dislike](/dislike) - command to dislike some post, same format as like:
*/dislike anon* - your name will not be saved in db and nobody will know who did that dislike
You'll receive short description of last 10 posts and you need to choice which one you dislike.
After that you'll receive ethereum address where you need to send any amount of ethereum depends how much you disliked the message.
This money will go to project donation wallet and the same amount will be taken from post's balance.
If post's balance equal 0, post will be deleted, so you can delete some post with dislike if you're ready to pay enough for that.

* === EXAMPLES: === *

_case 1:_
- Alice posts message "Hello idiots" with 0.1ETH, *balance = 0.1ETH*
- Bob dislikes the message with 0.03ETH, *balance = 0.07ETH*
- Alice saw it and she tries to protect her post, she does like with 0.05ETH, *balance = 0.12ETH*
- The message made Charlie mad and he dislikes the post with 0.13ETH, *balance = -0.01ETH*, post is deleted

_case 2:_
- Alice posts message "Hello guys, have a good day" with 0.1ETH, *balance = 0.1ETH*
- Bob likes the message with 0.08ETH, *balance = 0.18ETH*
- Charlie likes the message with 0.2ETH, *balance = 0.38ETH*
- Alice withdraws profit 0.28ETH, *balance = 0.1ETH*

* === ADDITIONAl === *

You can use message forwarding to like, dislike or withdraw. You need to choice post in channel and forward it to bot.
Don't type message, just send forwarded message. if bot recognizes post correct it asks you send command.
It could like, dislike and withdraw. You can use command's arguments as well.

You can dislike any posts, even channel admin's posts. 
All admin's posts have important information, that's why they have 10ETH on balance to protect them from instant deleting.

if you have some questions or proposals welcome to [LibertatemXTalks](https://t.me/joinchat/B3hiAA3VYCTI6fFKvb5MWQ)
