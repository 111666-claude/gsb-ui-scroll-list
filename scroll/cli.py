"""命令行入口：跑虚拟列表样例。"""

import argparse

from .core import ListView


def build_parser():
    parser = argparse.ArgumentParser(prog="ui-scroll-list", description="列表虚拟化")
    parser.add_argument("--sample", default="window",
                        help="window / clamp / pool / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "window":
        view = ListView(row_height=20, viewport_height=100, pool_size=6)
        view.set_items(["i-%d" % index for index in range(10)])
        print("visible=%d" % len(view.visible()))
    elif args.sample == "clamp":
        view = ListView(row_height=20, viewport_height=100, pool_size=6)
        view.set_items(["a", "b", "c"])
        view.scroll_to(500)
        print("offset=%d visible=%d" % (view.offset, len(view.visible())))
    elif args.sample == "pool":
        view = ListView(row_height=20, viewport_height=60, pool_size=3)
        view.set_items(["i-%d" % index for index in range(100)])
        for offset in (0, 60, 120):
            view.scroll_to(offset)
            view.render()
        print("active=%d" % view.active_rows())
    elif args.sample == "scan":
        view = ListView(row_height=20, viewport_height=60, pool_size=3)
        view.set_items(["i-%d" % index for index in range(3000)])
        for _ in range(3000):
            view.visible()
        print("scanned=%d" % view.scanned_count())
    else:
        raise SystemExit("需要 --sample window|clamp|pool|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
