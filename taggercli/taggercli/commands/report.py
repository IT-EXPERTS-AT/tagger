#
# Copyright (c) 2020 it-eXperts IT-Dienstleistungs GmbH.
#
# This file is part of tagger
# (see https://github.com/IT-EXPERTS-AT/tagger).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import List, Dict, Any, Optional

import typer
from itertools import groupby
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from taggercore.model import ResourceWithTagDiffs, Tag
from taggercore.usecase import scan_and_compare_resources

from taggercli.commands.util import print_tags
from taggercli.config import get_config, init_config

console = Console()

report_group = typer.Typer()
TAGGERCLI_DIR = Path(find_spec("taggercli").origin).parent
TEMPLATE_PATH = TAGGERCLI_DIR.joinpath("templates")
TEMPLATE_FILE_NAME = "template_report.html"
REPORT_FILE_NAME = "report.html"
tags = [Tag("Project", "CRM"), Tag("Owner", "Alice"), Tag("Cost-center", "Sales")]


@report_group.command("create")
def create_report_from_cli(
    region: Optional[str] = typer.Option(None, help="AWS region code"),
    output_path: Optional[str] = typer.Option(None, help="output path for the created html report"),
):
    init_config()
    config = get_config()
    account_id = config.account_id
    if not region:
        region = config.default_region
    tags = config.tags
    if not tags:
        console.print("No Tags found. Please specify them in your config file")
    print_tags(console, "Creating report with the following tags", tags)
    resources_with_diffs = scan_and_compare_resources(region, tags)
    console.print("Scanning completed")
    console.print(f"Found {len(resources_with_diffs)} resources")
    dashboard_data = prepare_data_for_dashboard_template(
        account_id, datetime.now(timezone.utc), resources_with_diffs
    )
    rendered_report = render_template(**dashboard_data)
    write_report(rendered_report, output_path)


def render_template(**kwargs) -> str:
    template = Environment(loader=FileSystemLoader(TEMPLATE_PATH)).get_template(
        TEMPLATE_FILE_NAME
    )
    return template.render(
        metrics_by_service=kwargs["metrics_by_service"],
        account_id=kwargs["account_id"],
        creation_datetime=kwargs["creation_datetime"],
        resources_by_service=kwargs["resources_by_service"],
    )


def prepare_data_for_dashboard_template(
    account_id: str,
    creation_datetime: datetime,
    resources_with_diffs: List[ResourceWithTagDiffs],
) -> Dict[str, Any]:
    resources_by_service = {
        key: list(resources)
        for key, resources in groupby(resources_with_diffs, lambda x: x.service)
    }
    resources_sorted_by_type_within_service = {
        k: v for k, v in resources_by_service.items()
    }
    metrics_by_service = metrics_for_dashboard_by_service(resources_by_service)
    return {
        "account_id": account_id,
        "creation_datetime": creation_datetime.strftime("%c (%Z)"),
        "metrics_by_service": metrics_by_service,
        "resources_by_service": resources_sorted_by_type_within_service,
    }


def metrics_for_dashboard_by_service(
    resources_by_service: Dict[str, List[ResourceWithTagDiffs]]
) -> Dict[str, Dict[str, int]]:
    metrics_by_service = {}

    for service, resources in resources_by_service.items():
        number_of_resources = len(resources)
        number_of_resources_tagged_properly = len(
            [resource for resource in resources if resource.properly_tagged]
        )
        metrics_by_service[service] = {
            "number_of_resources": number_of_resources,
            "number_of_resources_tagged_properly": number_of_resources_tagged_properly,
            "ratio_tagged_properly": number_of_resources_tagged_properly
            / number_of_resources,
        }
    return metrics_by_service


def write_report(html_report: str, output_path: str = None):
    if output_path:
        file_path = Path(output_path).joinpath(REPORT_FILE_NAME)
    else:
        file_path = REPORT_FILE_NAME
    with open(file_path, "w") as result_file:
        result_file.write(html_report)
    console.print(
        f"Created report under [default]{file_path}[/default] successfully",
        style="bold green",
    )
