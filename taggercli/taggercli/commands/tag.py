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
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from taggercore.model import Resource, Tag, TaggingResult
from taggercore.usecase import scan_region_and_global
from taggercore.usecase.perform_tagging import perform_tagging

from taggercli.commands.util import print_tags
from taggercli.config import get_config, init_config

console = Console()

tag_group = typer.Typer()


@tag_group.command("all")
def tag_all(region: Optional[str] = typer.Option(None, help="AWS region code")):
    init_config()
    config = get_config()
    if region is None:
        region = config.default_region
    resources = scan_region_and_global(region)
    regional_resources = resources[region]
    global_resources = resources["global"]
    console.print(f"Scanning completed", style="bold green")
    console.print(
        f"Found [green]{len(regional_resources)}[/green] resources in region [default]{region}[/default]"
    )
    console.print(f"Found [green]{len(global_resources)}[/green] global resources")
    if typer.confirm("Show detailed resource list?"):
        show_detailed_tables(region, regional_resources, global_resources)
    tags = config.tags
    print_tags(console, "Found following tags", tags)
    if typer.confirm("Do you want to apply those tags ?"):
        result = apply_tags(regional_resources + global_resources, tags)
        print_tagging_result(result)


def show_detailed_tables(
    region: str, regional_resources: List[Resource], global_resources: List[Resource]
) -> None:
    regional_table = create_table(f"Resource in region {region}", regional_resources)
    global_table = create_table("Global resources", global_resources)
    console.print(regional_table)
    console.print(global_table)


def create_table(title: str, resources: List[Resource]) -> Table:
    table = Table(title=title)
    table.add_column("Service")
    table.add_column("Type")
    table.add_column("Arn")
    table.add_column("Current Tags")

    for resource in resources:
        table.add_row(
            resource.service,
            resource.resource_type,
            resource.arn,
            ", ".join([repr(tag) for tag in resource.current_tags]),
        )
    return table


def apply_tags(resources: List[Resource], tags: List[Tag]) -> TaggingResult:
    return perform_tagging(resources, tags)


def print_tagging_result(tagging_result: TaggingResult) -> None:
    console.print(
        f"Tagged [green]{len(tagging_result.successful_arns)}[/green] resources successfully"
    )
    console.print(
        f"Failed to tag [default]{len(tagging_result.failed_arns)}[/default] resources"
    )
    for failed_resource, error_msg in tagging_result.failed_arns.items():
        console.print(f"Resource {failed_resource}: [red]{error_msg}[/red]")
