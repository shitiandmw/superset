/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import { render, screen } from 'spec/helpers/testing-library';
import { DndItemType } from 'src/explore/components/DndItemType';
import DatasourcePanelDragOption from '.';

test('should render', async () => {
  render(
    <DatasourcePanelDragOption
      value={{ metric_name: 'test', uuid: '1' }}
      type={DndItemType.Metric}
    />,
    { useDnd: true },
  );

  expect(
    await screen.findByTestId('DatasourcePanelDragOption'),
  ).toBeInTheDocument();
  expect(screen.getByText('test')).toBeInTheDocument();
});

test('should have attribute draggable:true', async () => {
  render(
    <DatasourcePanelDragOption
      value={{ metric_name: 'test', uuid: '1' }}
      type={DndItemType.Metric}
    />,
    { useDnd: true },
  );

  expect(
    await screen.findByTestId('DatasourcePanelDragOption'),
  ).toHaveAttribute('draggable', 'true');
});
