import requests
import argparse
import json
import logging
import time
from typing import List
from rich.logging import RichHandler
from rich.traceback import install as RichTracebackInstall
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

API_BANGUMI_USER = "https://api.bilibili.com/pgc/review/user"
API_SHORT_REVIEWS = "https://api.bilibili.com/pgc/review/short/list"
API_LONG_REVIEWS = "https://api.bilibili.com/pgc/review/long/list"

RichTracebackInstall()


def fetchReviews(log: logging.Logger, api_path: str, bangumi_id: int, user_agent: str, interval: float, reviews_number: int) -> List[int]:
    reviews_score_list: List[int] = []
    review_cursor: int = -1

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(None),
        MofNCompleteColumn(),
        transient=True
    ) as progress:
        task = progress.add_task("[red]Fetching reviews", total=-1)
        while review_cursor != 0 and (reviews_number <= 0 or progress.tasks[task].completed < reviews_number):
            cache: List[int] = []

            with requests.get(
                api_path,
                params={
                    "media_id": bangumi_id,
                    "cursor": None if review_cursor <= 0 else review_cursor,
                    "ps": 20
                },
                headers={"User-Agent": user_agent}
            ) as res:
                parsed_content = json.loads(res.content)

                assert parsed_content["code"] == 0

                for review in parsed_content["data"]["list"]:
                    cache.append(review["score"])
                    log.debug(f"Review {review['review_id']}: {str(review['score']).zfill(2)} @{review['author']['uname']}")

                review_cursor = parsed_content["data"]["next"]
                reviews_score_list.extend(cache)
                progress.update(
                    task,
                    completed=len(reviews_score_list),
                    total=parsed_content["data"]["total"]
                          if reviews_number <= 0 or parsed_content["data"]["total"] <= reviews_number
                          else reviews_number
                )
            time.sleep(interval)
        if len(reviews_score_list) < progress.tasks[task].total: #type: ignore
            log.warning((
                f"There are {len(reviews_score_list)} comments; "
                f"however, there should be {progress.tasks[task].total} comments according to the API."
            ))
    return reviews_score_list


def _main(args: argparse.Namespace, log: logging.Logger) -> None:
    # Verify Arguments
    if args.short_reviews < 20 and args.short_reviews != -1:
        args.short_reviews = 20
        log.warning("--short-reviews should be more than 20.")
    if args.long_reviews < 20 and args.long_reviews != -1:
        args.long_reviews = 20
        log.warning("--long-reviews should be more than 20.")

    # Get Information
    log.info(time.ctime())
    with requests.get(
        API_BANGUMI_USER,
        params={"media_id": args.bangumi},
        headers={"User-Agent": args.user_agent}
    ) as res:
        parsed_content = json.loads(res.content)
        assert parsed_content["code"] == 0
        log.info((
            f"Bangumi Name: {parsed_content['result']['media']['title']}\n"
            f"Bangumi Type: {parsed_content['result']['media']['type_name']}\n"
            f"Bangumi Score (Official, may be fake): {parsed_content['result']['media']['rating']['score']} "
            f"({parsed_content['result']['media']['rating']['count']} reviews)"
        ))

    # Fetch Short Reviews
    log.info("Fetching short reviews...")
    short_reviews_score_list = fetchReviews(log, API_SHORT_REVIEWS, args.bangumi,
                                            args.user_agent, args.interval, args.short_reviews)
    short_reviews_average_score = sum(
        short_reviews_score_list)/len(short_reviews_score_list)
    log.info(
        "[bold]Short reviews fetch [green]completed[/green].[/]\n"
        "Average score: "
        "{:.2f} (based on {} reviews)".format(
            short_reviews_average_score, len(short_reviews_score_list)),
        extra={"markup": True}
    )
    
    # Fetch Long Reviews
    log.info("Fetching long reviews...")
    long_reviews_score_list = fetchReviews(log, API_LONG_REVIEWS, args.bangumi,
                                            args.user_agent, args.interval, args.long_reviews)
    long_reviews_average_score = sum(
        long_reviews_score_list)/len(long_reviews_score_list)
    log.info(
        "[bold]Long reviews fetch [green]completed[/green].[/]\n"
        "Average score: "
        "{:.2f} (based on {} reviews)".format(
            long_reviews_average_score, len(long_reviews_score_list)),
        extra={"markup": True}
    )

    # Final Average Score
    log.info(
        "Final Score: {:.2f} ".format(
            (long_reviews_average_score+short_reviews_average_score)/2)
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'bangumi',
        type=int,
        help="The ID of the bangumi",
    )
    parser.add_argument(
        '--user-agent',
        type=str,
        default="mozilla/5.0 (windows nt 10.0 win64 x64) applewebkit/537.36 (khtml, like gecko) chrome/107.0.0.0 safari/537.36",
        help="User agent"
    )
    parser.add_argument(
        '--short-reviews',
        type=int,
        default=-1,
        help="Number of short reviews collected(-1 means all)"
    )
    parser.add_argument(
        '--long-reviews',
        type=int,
        default=-1,
        help="Number of long reviews collected(-1 means all)"
    )
    parser.add_argument(
        '--level',
        type=str,
        default="INFO",
        choices=logging._nameToLevel.keys(),
        help="Log output level"
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=.5,
        help="Interval between two requests"
    )
    parser.add_argument(
        '--no-log-file',
        action="store_true",
        help="No bangumi-score.log file"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging._nameToLevel[args.level],
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(),
            logging.FileHandler("bangumi-score.log", mode='w', encoding='utf-8')
            if not args.no_log_file 
            else logging.NullHandler()
        ]
    )
    log = logging.getLogger()

    _main(args, log)
