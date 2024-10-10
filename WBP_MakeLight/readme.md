# WBP_MakeLight
![image](https://github.com/user-attachments/assets/521893a1-b458-4407-b31e-a6851bf8b539)


## 목차

1. 파일 구성 및 설치 방법
2. UI 및 기능 소개  
   2-1. MakeLight  
   2-2. MakeSubSeq
3. 사용 예시
4. 버전 기록

## 1. 파일 구성 및 설치 방법

[**다운로드**](https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/WBP_MakeLight/WBP_MakeLight.uasset) https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/WBP_MakeLight/WBP_MakeLight.uasset


![image](https://github.com/user-attachments/assets/4cbf95e2-610e-46ee-aa15-5d95def5a2d2)

![image](https://github.com/user-attachments/assets/c7c7c6cc-63f9-4af1-bec7-75c05e1aea09)


- WBP_MakeLight.uasset를 프로젝트 폴더의 Content 폴더 하위의 원하는 위치에 넣는다.

![image](https://github.com/user-attachments/assets/d80da976-9f4e-46ee-8cca-227783010b1f)


- WBP_MakeLight 위젯을 찾아 우클릭 후 에디터 유틸리티 실행을 누른다.

![image (1)](https://github.com/user-attachments/assets/59a38bed-5742-4f83-b2c5-34953c7bb62f)



## 2. UI 및 기능 소개

![image](https://github.com/user-attachments/assets/521893a1-b458-4407-b31e-a6851bf8b539)


## 2-1. MakeLight
- 조명 종류 : 생성할 라이트의 종류를 선택한다. Spot, Rect, Point

- 조명 용도 : 생성할 라이트의 용도를 선택한다.  
Key, Fill, LeftRim, RightRim - 사전 설정된 위치로 생성된다.  
ThreePoint - Key, Fill, LeftRim, RightRim을 모두 한번에 생성한다.  
None - 원점에 생성한다.  

- 부착할 본 : 어태치할 본을 선택한다.  
Head, Neck, Spine - 각 Bip001-Head, Bip001-Neck Bip001-Spine2에 어태치한다.  
None - 본이 아닌 액터에 어태치한다.  
Custom - 우측의 “Custom 본 이름 입력” 창에 입력된 본의 이름으로 어태치한다.  

- 스켈레탈 메시 : 캐릭터를 블루프린트로 사용해야 할 때, 하위에 있는 스켈레탈 메시를 선택한다.
![image](https://github.com/user-attachments/assets/2648129d-d7d4-4c43-9086-387960427d3d)

- 스켈레탈 메시 찾기 : 선택한 블루프린트에서 스켈레탈 메시를 찾는다.
![스켈레탈메시찾기](https://github.com/user-attachments/assets/e024b6ab-a407-4e7c-ae57-9961ec7f035f)

- 조명 생성 및 부착 : 설정된 라이트를 생성하고 선택한 액터에 어태치한다.

- 기존 조명 부착 : 선택한 액터와 라이트를 어태치한다. **(꼭 액터를 첫번째로 선택한다!!)**










## 2-2. MakeSubSeq

### 실행법
   


1. 서브 시퀀스를 생성 할 샷 시퀀스를 엽니다.  
   ![image](https://github.com/user-attachments/assets/29cf4424-d181-40d0-971a-0d6f3b7ea19d)  


   ![image (1)](https://github.com/user-attachments/assets/59a38bed-5742-4f83-b2c5-34953c7bb62f)


3. WBP_MakeLight 위젯을 우클릭하여 실행합니다.

   ![image](https://github.com/user-attachments/assets/cd47a8e1-9a13-4639-b643-de16e234a959)


4. 위젯 선택 버튼에서 MakeSubSeq를 누릅니다.

   ![image (6)](https://github.com/user-attachments/assets/69e4e119-0240-4c31-a91f-398daaf38e32)


5. 아래 설정법을 참고하여 Make를 눌러 생성합니다.


## 2-2. MakeSubSeq

### 설정법
1. 프로젝트

   ![image (3)](https://github.com/user-attachments/assets/fa19b96a-e5fe-4db4-9b68-873e04c5dc04)


   프로젝트별 네이밍 컨벤션에 맞추기 위한 설정입니다. (현재 Default로 고정)



2. 프로젝트 네임

   ![image (4)](https://github.com/user-attachments/assets/a3efdd3b-2954-4d16-8fb4-88da948b6a70)


   체크 시 서브시퀀스 이름에 프로젝트 이름을 추가하는 설정입니다.

   ex)

   켰을때 : LIT_SUB_2024_Enchantress_Shot_01_01

   껐을때 : LIT_SUB_Shot_01_01



3. 파트
   
   ![image (5)](https://github.com/user-attachments/assets/420f45ab-886e-457a-95a2-5758588343df)


   원하는 파트만 선택해 생성할 수 있습니다.

  
4. 생성
   
   ![image (6)](https://github.com/user-attachments/assets/27b1ce50-9037-4ce4-828b-399aa8e4b890)




   Make 버튼을 누르면 생성을 시작합니다.
   **현재 열려있는 시퀀스로 실행됩니다!**



## 2-2. MakeSubSeq

### 기능
1. 폴더구조

   ![image (7)](https://github.com/user-attachments/assets/78a4b995-fc22-4460-ada3-b390b885edb7)

   폴더 구조는 다음과 같이 생성됩니다.

   Shot의 위치에서 실행하면 하위 구조는 자동 생성됩니다.

   프로젝트 이름은 Shot폴더의 상위 폴더의 이름을 가지고 옵니다.

  

2. 레벨라이트 포함

   ![image (8)](https://github.com/user-attachments/assets/1baef0ef-73fd-48d5-a88f-a6fb7890f547)

   LIT 서브시퀀스의 경우에는 레벨에 포함된 라이트를 자동으로 연결합니다.

   기본 라이트 세팅이 레벨에 없을 경우 ‘스포너블’로 생성합니다.

  

3. 섹션 범위 설정

   ![image](https://github.com/user-attachments/assets/ce40dc11-864f-42fd-a513-24da2e2428ea)

   Playback 범위에 맞춰 자동 등록됩니다. (웜업세팅을 고려해 ±50f으로 설정됩니다.)

  

4. 네이밍

   ![image (10)](https://github.com/user-attachments/assets/b82204e5-8d12-4320-a6e0-d98faeee6d21)

   중복된 이름이 있을 경우 경고 창을 팝업합니다. 예를 누르면 다음 번호로 생성,

   아니오를 누르면 작업이 취소됩니다.


## 3. 사용 예시

- 기본 라이팅 세팅하기
    
   ![기본라이팅세팅하기](https://github.com/user-attachments/assets/04196436-afba-4f0b-a5cb-09e2616e94d8)


- 머리에 림라이트 생성하기
    
   ![머리림라이트생성하기](https://github.com/user-attachments/assets/fa4a8587-4174-4fa0-a9a6-c7e4ffd3660e)
    

- 기존 조명을 어태치하기  
  **위젯버전에서는 스켈레탈메시 또는 캐릭터 블루프린트를 첫번째로 선택한다!!**
    
   ![기존조명을어태치하기](https://github.com/user-attachments/assets/fd6aead0-6acd-470c-b4b3-05d75d312534)
    

- 원하는 본에 어태치하기
    
   ![원하는본에어태치하기](https://github.com/user-attachments/assets/4058dc40-2f87-48ea-ba1f-bb0af772ccbb)
    

## 4. 버전 기록

24.09.23 Alpha1 : https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/MakeLight/MakeLight_Alpha1.zip  
24.10.04 Widget1:
https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/24498cd2b81c637411fc9da226059fa3f9c01acd/WBP_MakeLight/WBP_MakeLight.uasset  
24.10.07 widget2:
https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/WBP_MakeLight/WBP_MakeLight.uasset

24.10.10 widget3:  
https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/WBP_MakeLight/WBP_MakeLight.uasset  
![image](https://github.com/user-attachments/assets/20ab3a83-b297-4907-82fd-0b95c9ff5f5c)  
숨겨진 액터 관련 옵션 추가.
