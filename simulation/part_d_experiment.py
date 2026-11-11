"""Part D Option 3: four fitted/raw methods, no oracle ellipse information."""
from .experiment import D_DESIGN as DEFAULT_DESIGN, run_experiment as _run, main


def run_experiment(methods=None, design=None, checkpoint=None, smoke=False):
    return _run('D', design, checkpoint, smoke, methods)


if __name__ == '__main__':
    main('D')
