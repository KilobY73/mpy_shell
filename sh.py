import os
import _thread

env = {"PWD": "/", "PATH": ".", "PS1": "\W $ "}
builtin_cmd = ("cd", "ls", "exit", "echo", "rm", "mv", "cp", "cat", "mkdir")

try:
  exit
except:
  def exit(param):
    raise EOFError

def execute(param):
  if len(param) == 0:
    return
  if param[0] in builtin_cmd:
    exec(param[0] + '(' + str(param) + ')')
    return
  try:
    f = open(env["PATH"] + '/' + param[0], 'r')
    exec(f.read())
    f.close()
  except KeyboardInterrupt:
    pass
  except:
    print(param[0] + ": command not found")

def parse(paramtuple):
  param = list(paramtuple)
# Replace variable
  for i in range(0, len(param)):
    if '$' in param[i]:
      for j in param[i].split('$'):
        varname = '$'
        if j == "":
          continue
        val = ""
        if j[0] == '{':
          try:
            j = j[1:j.index('}')]
            varname += '{' + j + '}'
          except:
            pass
        else:
          varname += j
        if j in env:
          val = env[j]
          param[i] = param[i].replace(varname, val)
  execute(param)

def readcmd():
  command = input(env["PS1"].replace("\W", env["PWD"]))
  if command == "":
    return
# Multiline
  while command[-1] == '\\':
    command = command[0:-1] + input('> ')
  cmds = command.split('&')
  for i in range(0, len(cmds) - 1):
    cmds[i] += '&'
  param = []
  for cmd in cmds:
    for i in cmd.split(' '):
      if i == '':
        continue
      if '&' in i:
        if i.split('&')[0] != '':
          param.append(i.split('&')[0])
        _thread.start_new_thread(parse, (tuple(param),))
        param = []
      else:
        param.append(i)
  parse(tuple(param))

def builtin_isdir(path):
  try:
    os.listdir(path)
    return True
  except:
    return False

def builtin_getpath(paramstr):
  path = []
  if paramstr[0] != '/':
    for i in env["PWD"].split('/'):
      if i != "":
        path.append(i)
  for i in paramstr.split('/'):
    if len(path) != 0 and i == "..":
      path.pop()
    if i != '.' and i != "..":
      path.append(i)
  pathstr = ""
  for i in path:
    pathstr += '/' + i
  if pathstr == '':
    return '/'
  return pathstr

def cd(param):
  if len(param) > 2:
    print("cd: too many arguments")
    return
  if len(param) == 1 or param[1] == "":
    env["PWD"] = '/'
    return
  path = builtin_getpath(param[1])
  if not builtin_isdir(path):
    print("cd: %s: No such file or directory" % param[1])
    return
  env["PWD"] = path

def ls(param):
  path = env["PWD"]
  if len(param) != 1:
    path = builtin_getpath(param[1])
  res = ""
  content = []
  try:
    content = os.listdir(path)
  except:
    print("ls: cannot access '%s': No such file or directory" % param[1])
  content.sort()
  for i in content:
    if i[0] != '.':
      res += i + '\t'
  print(res)

def cp(param):
  if len(param) == 1:
    print("cp: missing file operand")
    return
  if len(param) == 2:
    print("cp: missing destination file operand after '%s'" % param[1])
    return
  try:
    infd = open(builtin_getpath(param[1]), 'r')
    outfd = open(builtin_getpath(param[2]), 'w')
    outfd.write(infd.read())
    infd.close()
    outfd.close()
  except:
    print("cp: cannot create regular file '%s': No such file or directory" % param[2])

def mv(param):
  if len(param) == 1:
    print("mv: missing file operand")
    return
  if len(param) == 2:
    print("mv: missing destination file operand after '%s'" % param[1])
    return
  try:
    os.rename(builtin_getpath(param[1]), builtin_getpath(param[2]))
  except:
    print("mv: cannot move '%s' to '%s': No such file or directory" % (param[1], param[2]))
  
def rm(param):
  recursive = False
  for i in param:
    if i == "-r":
      param.remove(i)
      recursive = True
  if len(param) == 1:
    print("rm: missing operand")
    return
  if recursive:
    for i in param[1:]:
      stack = [builtin_getpath(i)]
      if not builtin_isdir(stack[0]):
        print("rm: cannot remove '%s': No such file or is a directory" % i)
        return
      while len(stack) != 0:
        current = stack.pop()
        if builtin_isdir(current):
          try:
            os.rmdir(current)
          except:
            stack.append(current)
            for j in os.listdir(current):
              stack.append(current + '/' + j)
        else:
          os.remove(current)
  else:
    for i in param[1:]:
      try:
        os.remove(builtin_getpath(i))
      except:
        print("rm: cannot remove '%s': No such file or is a directory" % i)

def mkdir(param):
  if len(param) == 1:
    print("mkdir: missing operand")
    return
  for i in param[1:]:
    try:
      os.mkdir(builtin_getpath(i))
    except OSError:
      print("mkdir: cannot create directory ‘%s’: No such file or directory" % i)
    except:
      print("mkdir: cannot create directory ‘%s’: File exists" % i)

def cat(param):
  if len(param) == 1:
    print("cat: function not implemented")
    return
  for i in param[1:]:
    try:
      f = open(builtin_getpath(i))
      for l in f:
        print(l, end = '')
      f.close()
    except:
      print("cat: %s: No such file or directory" % i)

def echo(param):
  if len(param) == 1:
    print()
    return
  res = ""
  for i in param[1:]:
    res += i + ' '
  print(res)

def start():
  while True:
    try:
      readcmd()
    except KeyboardInterrupt:
      print("^C")
    except EOFError:
      print('\nexit')
      break
