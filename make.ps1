param(
    [ValidateSet('run','build')]
    [string]$tarefa = 'run'
)

switch ($tarefa) {
    'run'   { python app/main.py }
    'build' { pyinstaller build/assinar.spec }
}
