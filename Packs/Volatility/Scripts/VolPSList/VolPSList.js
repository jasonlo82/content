var cmdline = 'pslist';
var out = executeCommand('Volatility', {memdump:args.memdump, profile:args.profile, system: args.system, cmd:cmdline});
return out;
