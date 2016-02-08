"""
    Annuaire avec envoi de mails pour GNU/Linux Magazine

    Author: Tristan Colombo <tristan@gnulinuxmag.com>
                            (@TristanColombo)

    Date: 17-12-2015

    Last modification: 17-12-2015

    Licence: GNU GPL v3 (voir fichier gpl_v3.txt joint)
"""

import argparse


def cli_mode(args):
    print('Mode CLI')
    print('Contact:', args.name)
    print('Temps: ', end='')
    if args.sun:
        print('soleil')
    else:
        print('pluie')


def text_mode(args):
    print('Interface textuelle')


def gui_mode(args):
    print('Interface graphique')


if __name__ == '__main__':
    """
        Création du parser d'arguments pour la ligne
        de commandes
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Commandes')

    # Mode CLI
    cli_parser = subparsers.add_parser('cli', help='Mode ligne de commandes')
    cli_parser.add_argument('name', help='Prénom et nom du contact')
    cli_parser.add_argument('-s', '--soleil', action='store_true',
                            default=False, dest='sun',
                            help='Temps à insérer dans le fichier pdf')
    cli_parser.set_defaults(func=cli_mode)

    # Mode texte
    text_parser = subparsers.add_parser('text',
                                        help="Mode interface textuelle")
    text_parser.set_defaults(func=text_mode)

    # Mode graphique
    gui_parser = subparsers.add_parser('gui', help="Mode interface graphique")
    gui_parser.set_defaults(func=gui_mode)

    args = parser.parse_args()
    args.func(args)
