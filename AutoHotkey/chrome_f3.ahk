#SingleInstance, force
chrome_find_f()
{
	SetTitleMatchMode 2
	IfWinActive, Google Chrome
	{
	  Clipboard=
	  Send, ^c
	  if Clipboard=
	  {
		Send, ^f
		return
	  }
	  Send, ^f
	  Send, ^v
	  Send, ^a
	  return
	}
	else
	{
	  Send, ^f
	  return
	}
	;Esc::ExitApp
}

chrome_find_F3()
{
	SetTitleMatchMode 2
	IfWinActive, Google Chrome
	{
	  Clipboard=
	  Send, ^c
	  if Clipboard=
	  {
		Send, {F3}
		return
	  }
	  Send, ^f
	  Send, ^v
	  Send, ^a
	  return
	}
	else
	{
	  Send, {F3}
	  return
	}
	;Esc::ExitApp
}

$^f:: chrome_find_f()
$F3:: chrome_find_F3()
