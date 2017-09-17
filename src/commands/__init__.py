from commands import debug, main, post, reaction, settings, withdraw


commands = (
    main.StartCommand,
    main.AboutCommand,
    main.InfoCommand,
    post.PostCommand,
    reaction.LikeCommand,
    reaction.DislikeCommand,
    withdraw.WithdrawCommand,
    settings.SettingsCommand,
    main.PingCommand,
    debug.ConfirmCommand,
    main.CancelCommand,
)
