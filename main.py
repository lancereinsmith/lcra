import asyncio

import click
import uvicorn
from rich.console import Console

from scraper import LCRAFloodDataScraper

console = Console()


@click.group()
def cli():
    """LCRA Flood Status CLI"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to serve the API on")
@click.option("--port", default=8080, help="Port to serve the API on")
def serve(host, port):
    """Serve the LCRA Flood Status API"""
    uvicorn.run("api:app", host=host, port=port, reload=True)


@cli.command(name="get")
@click.option("--report", is_flag=True, help="Extract the full flood operations report")
@click.option("--lake-levels", is_flag=True, help="Extract current lake levels")
@click.option(
    "--river-conditions", is_flag=True, help="Extract current river conditions"
)
@click.option(
    "--floodgate-operations", is_flag=True, help="Extract floodgate operations"
)
def get(report, lake_levels, river_conditions, floodgate_operations):
    """Extract LCRA flood status data and print to stdout"""

    async def run_extract():
        async with LCRAFloodDataScraper() as scraper:
            if report:
                data = await scraper.scrape_all_data()
                console.print(data.model_dump(), soft_wrap=True)
            if lake_levels:
                data = await scraper.scrape_lake_levels()
                console.print([d.model_dump() for d in data], soft_wrap=True)
            if river_conditions:
                data = await scraper.scrape_river_conditions()
                console.print([d.model_dump() for d in data], soft_wrap=True)
            if floodgate_operations:
                data = await scraper.scrape_floodgate_operations()
                console.print([d.model_dump() for d in data], soft_wrap=True)
            if not any([report, lake_levels, river_conditions, floodgate_operations]):
                console.print(
                    "[yellow]Specify at least one data type to extract. Use --help for options.[/yellow]"
                )

    asyncio.run(run_extract())


if __name__ == "__main__":
    cli()
